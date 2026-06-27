import os
import json
from datetime import datetime, timezone, timedelta
from flask import (
    Flask, request, render_template, redirect, url_for,
    send_file, jsonify, flash, abort
)
from config import Config
from models import db, Report, ChatMessage
from services import ai_service, report_service, insights_service
import io

app = Flask(__name__)
app.config.from_object(Config)

# Validate required environment variables at startup.
# Raises EnvironmentError with a clear message if GEMINI_API_KEY is missing.
Config.validate()

db.init_app(app)

with app.app_context():
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    db.create_all()

# Simple in-memory cache for /insights (avoids a Gemini call on every page load)
_insights_cache = {'data': None, 'stats': None, 'expires': None}


# ── HOME ──────────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    total = Report.query.count()
    recurring = Report.query.filter_by(is_recurring=True).count()
    resolved = Report.query.filter_by(status='resolved').count()
    recent = Report.query.order_by(Report.created_at.desc()).limit(4).all()
    return render_template(
        'home.html',
        total=total,
        recurring=recurring,
        resolved=resolved,
        recent=recent,
    )


# ── REPORT SUBMISSION ─────────────────────────────────────────────────────────

@app.route('/report', methods=['GET'])
def report_form():
    return render_template('report.html')


@app.route('/report', methods=['POST'])
def report_submit():
    if 'image' not in request.files or request.files['image'].filename == '':
        flash('Please upload a photo of the issue.', 'error')
        return redirect(url_for('report_form'))

    image_file = request.files['image']
    location_text = request.form.get('location_text', '').strip()
    area_type = request.form.get('area_type', 'residential')

    if not location_text:
        flash('Please enter the issue location.', 'error')
        return redirect(url_for('report_form'))

    form_data = {
        'location_text': location_text,
        'area_type': area_type,
        'latitude': request.form.get('latitude', '').strip(),
        'longitude': request.form.get('longitude', '').strip(),
    }

    try:
        report = report_service.process_report_submission(form_data, image_file)
        return redirect(url_for('confirmation', tracking_id=report.tracking_id))
    except ValueError as e:
        flash(str(e), 'error')
        return redirect(url_for('report_form'))
    except Exception as e:
        app.logger.error(f'Report submission error: {e}')
        flash('An error occurred while processing your report. Please try again.', 'error')
        return redirect(url_for('report_form'))


# ── CONFIRMATION ──────────────────────────────────────────────────────────────

@app.route('/confirmation/<tracking_id>')
def confirmation(tracking_id):
    report = Report.query.filter_by(tracking_id=tracking_id).first_or_404()
    return render_template('confirmation.html', report=report)


# ── DOWNLOADS ─────────────────────────────────────────────────────────────────

@app.route('/download/<int:report_id>/letter')
def download_letter(report_id):
    report = db.get_or_404(Report, report_id)
    if not report.escalation_letter:
        abort(404)
    letter_bytes = report.escalation_letter.encode('utf-8')
    return send_file(
        io.BytesIO(letter_bytes),
        mimetype='text/plain',
        as_attachment=True,
        download_name=f'CivicLens_{report.tracking_id}_Escalation_Letter.txt',
    )


@app.route('/download/<int:report_id>/followup')
def download_followup(report_id):
    report = db.get_or_404(Report, report_id)
    if not report.followup_letter:
        abort(404)
    letter_bytes = report.followup_letter.encode('utf-8')
    return send_file(
        io.BytesIO(letter_bytes),
        mimetype='text/plain',
        as_attachment=True,
        download_name=f'CivicLens_{report.tracking_id}_FollowUp_Letter.txt',
    )


# ── COMMUNITY FEED ────────────────────────────────────────────────────────────

@app.route('/feed')
def feed():
    sort = request.args.get('sort', 'recurring')
    query = Report.query

    if sort == 'impact':
        query = query.order_by(Report.impact_score.desc(), Report.created_at.desc())
    elif sort == 'recent':
        query = query.order_by(Report.created_at.desc())
    elif sort == 'unresolved':
        query = query.filter(Report.status != 'resolved').order_by(Report.created_at.desc())
    else:  # default: recurring first
        query = query.order_by(
            Report.is_recurring.desc(),
            Report.impact_score.desc(),
            Report.created_at.desc()
        )

    reports = query.all()
    return render_template('feed.html', reports=reports, current_sort=sort)


# ── ISSUE DETAIL ──────────────────────────────────────────────────────────────

@app.route('/issue/<int:report_id>')
def issue_detail(report_id):
    report = db.get_or_404(Report, report_id)
    chat_messages = ChatMessage.query.filter_by(
        report_id=report_id
    ).order_by(ChatMessage.created_at).all()
    return render_template('issue_detail.html', report=report, chat_messages=chat_messages)


# ── CITIZEN AI ASSISTANT ──────────────────────────────────────────────────────

@app.route('/chat/<int:report_id>', methods=['POST'])
def chat(report_id):
    report = db.get_or_404(Report, report_id)
    data = request.get_json()
    if not data or not data.get('message', '').strip():
        return jsonify({'error': 'No message provided'}), 400

    user_message = data['message'].strip()

    history_rows = ChatMessage.query.filter_by(
        report_id=report_id
    ).order_by(ChatMessage.created_at).all()
    history = [{'role': m.role, 'content': m.content} for m in history_rows]

    ai_response = ai_service.chat_with_assistant(report, history, user_message)

    user_msg = ChatMessage(report_id=report_id, role='user', content=user_message)
    assistant_msg = ChatMessage(report_id=report_id, role='assistant', content=ai_response)
    db.session.add(user_msg)
    db.session.add(assistant_msg)
    db.session.commit()

    return jsonify({'response': ai_response})


# ── MAP ───────────────────────────────────────────────────────────────────────

@app.route('/map')
def map_view():
    return render_template('map.html')


@app.route('/map/data')
def map_data():
    reports = Report.query.filter(
        Report.latitude.isnot(None),
        Report.longitude.isnot(None)
    ).all()
    pins = []
    for r in reports:
        pins.append({
            'id': r.id,
            'tracking_id': r.tracking_id,
            'lat': r.latitude,
            'lng': r.longitude,
            'issue_type': r.issue_type or 'Unknown',
            'severity': r.severity or 3,
            'status': r.status,
            'location_text': r.location_text,
            'is_recurring': r.is_recurring,
        })
    return jsonify(pins)


# ── ADMIN ─────────────────────────────────────────────────────────────────────

@app.route('/admin')
def admin():
    """
    Admin dashboard. Displays all reports and stats.
    Follow-up generation is now triggered explicitly via /admin/run-followup
    rather than on every page load — preventing uncontrolled Gemini API calls.
    """
    total = Report.query.count()
    pending = Report.query.filter_by(status='reported').count()
    in_progress = Report.query.filter_by(status='in_progress').count()
    recurring = Report.query.filter_by(is_recurring=True).count()
    escalation_due = Report.query.filter_by(escalation_due=True).count()

    # Count overdue reports so the admin can see how many would be processed
    cutoff = datetime.now(timezone.utc) - timedelta(days=3)
    overdue_count = Report.query.filter(
        Report.status == 'in_progress',
        Report.followup_letter.is_(None),
        Report.created_at <= cutoff,
    ).count()

    reports = Report.query.order_by(Report.created_at.desc()).all()

    return render_template(
        'admin.html',
        reports=reports,
        total=total,
        pending=pending,
        in_progress=in_progress,
        recurring=recurring,
        escalation_due=escalation_due,
        overdue_count=overdue_count,
    )


@app.route('/admin/run-followup', methods=['POST'])
def admin_run_followup():
    """
    Explicitly trigger autonomous follow-up letter generation for overdue reports.
    Moved out of the GET /admin handler to prevent Gemini calls on every page load.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(days=3)
    overdue = Report.query.filter(
        Report.status == 'in_progress',
        Report.followup_letter.is_(None),
        Report.created_at <= cutoff,
    ).all()

    generated = 0
    for report in overdue:
        try:
            letter = ai_service.generate_followup_letter(report)
            report.followup_letter = letter
            report.followup_generated_at = datetime.now(timezone.utc)
            report.escalation_due = True
            db.session.commit()
            generated += 1
            app.logger.info(f'Follow-up generated for {report.tracking_id}')
        except Exception as e:
            app.logger.error(f'Follow-up generation failed for {report.tracking_id}: {e}')

    flash(f'Generated {generated} follow-up letter(s).', 'success')
    return redirect(url_for('admin'))


@app.route('/admin/update', methods=['POST'])
def admin_update():
    report_id = request.form.get('report_id')
    new_status = request.form.get('status')

    valid_statuses = {'reported', 'under_review', 'in_progress', 'resolved'}
    if not report_id or new_status not in valid_statuses:
        flash('Invalid update.', 'error')
        return redirect(url_for('admin'))

    report = db.get_or_404(Report, int(report_id))
    report.status = new_status

    if new_status == 'resolved':
        report.escalation_due = False

    db.session.commit()
    return redirect(url_for('admin'))


# ── INSIGHTS ──────────────────────────────────────────────────────────────────

@app.route('/insights')
def insights():
    """
    Civic health analytics. Caches the Gemini result for 10 minutes to avoid
    a billable API call on every page view.
    """
    if Report.query.count() == 0:
        return render_template('insights.html', insights=None, stats=None)

    now = datetime.now(timezone.utc)

    # Return cached result if still valid
    if (
        _insights_cache['data'] is not None
        and _insights_cache['expires'] is not None
        and now < _insights_cache['expires']
    ):
        return render_template(
            'insights.html',
            insights=_insights_cache['data'],
            stats=_insights_cache['stats'],
        )

    # Cache miss — call Gemini and store result
    stats = insights_service.get_aggregated_stats()
    civic_insights = ai_service.generate_civic_insights(stats)

    _insights_cache['data'] = civic_insights
    _insights_cache['stats'] = stats
    _insights_cache['expires'] = now + timedelta(minutes=10)

    return render_template('insights.html', insights=civic_insights, stats=stats)


@app.route('/insights/refresh', methods=['POST'])
def insights_refresh():
    """Force-expire the insights cache so the next /insights load fetches fresh data."""
    _insights_cache['data'] = None
    _insights_cache['stats'] = None
    _insights_cache['expires'] = None
    flash('Insights cache cleared. Reload the Insights page for fresh analysis.', 'success')
    return redirect(url_for('insights'))


# ── ENTRY POINT ───────────────────────────────────────────────────────────────

if __name__ == '__main__':
    app.run(debug=os.getenv('FLASK_DEBUG', 'false').lower() == 'true')
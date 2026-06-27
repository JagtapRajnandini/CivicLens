import os
import sys
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

from models import login_manager
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access the admin area.'
login_manager.login_message_category = 'error'



# Validate required environment variables at startup.
# SystemExit (not EnvironmentError) ensures gunicorn logs the message cleanly
# and exits with a non-zero code rather than crashing mid-request.
if not app.config.get('GEMINI_API_KEY'):
    print(
        "FATAL: GEMINI_API_KEY is not set. "
        "Add it to .env locally or to Render environment variables.",
        file=sys.stderr
    )
    sys.exit(1)

db.init_app(app)

with app.app_context():
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    db.create_all()

# Simple in-memory cache for /insights (avoids a Gemini call on every page load).
# Resets on worker restart — acceptable for a single-worker deployment.
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

    # Validate coordinates are present (now mandatory)
    latitude_raw = request.form.get('latitude', '').strip()
    longitude_raw = request.form.get('longitude', '').strip()
    if not latitude_raw or not longitude_raw:
        flash('Location coordinates are required. Use "Get My Location" or enter them manually.', 'error')
        return redirect(url_for('report_form'))

    form_data = {
        'location_text': location_text,
        'area_type': area_type,
        'latitude': latitude_raw,
        'longitude': longitude_raw,
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
    else:
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
    Admin dashboard. Requires admin login.
    Follow-up generation is triggered explicitly via /admin/run-followup.
    """
    from flask_login import current_user
    if not current_user.is_authenticated or not current_user.is_admin:
        flash('Admin access required.', 'error')
        return redirect(url_for('login'))

    total = Report.query.count()
    pending = Report.query.filter_by(status='reported').count()
    in_progress = Report.query.filter_by(status='in_progress').count()
    recurring = Report.query.filter_by(is_recurring=True).count()
    escalation_due = Report.query.filter_by(escalation_due=True).count()

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
    from flask_login import current_user
    if not current_user.is_authenticated or not current_user.is_admin:
        abort(403)

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
        except Exception as e:
            app.logger.error(f'Follow-up failed for {report.tracking_id}: {e}')

    flash(f'Generated {generated} follow-up letter(s).', 'success')
    return redirect(url_for('admin'))


@app.route('/admin/update', methods=['POST'])
def admin_update():
    from flask_login import current_user
    if not current_user.is_authenticated or not current_user.is_admin:
        abort(403)

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
    if Report.query.count() < 5:
        return render_template('insights.html', insights=None, stats=None,
                               min_reports_needed=5)

    now = datetime.now(timezone.utc)
    if (
        _insights_cache['data'] is not None
        and _insights_cache['expires'] is not None
        and now < _insights_cache['expires']
    ):
        return render_template(
            'insights.html',
            insights=_insights_cache['data'],
            stats=_insights_cache['stats'],
            min_reports_needed=None,
        )

    stats = insights_service.get_aggregated_stats()
    civic_insights = ai_service.generate_civic_insights(stats)

    _insights_cache['data'] = civic_insights
    _insights_cache['stats'] = stats
    _insights_cache['expires'] = now + timedelta(minutes=10)

    return render_template('insights.html', insights=civic_insights, stats=stats,
                           min_reports_needed=None)


@app.route('/insights/refresh', methods=['POST'])
def insights_refresh():
    from flask_login import current_user
    if not current_user.is_authenticated or not current_user.is_admin:
        abort(403)
    _insights_cache['data'] = None
    _insights_cache['stats'] = None
    _insights_cache['expires'] = None
    flash('Insights cache cleared. Reload the Insights page for fresh analysis.', 'success')
    return redirect(url_for('insights'))


# ── AUTH ──────────────────────────────────────────────────────────────────────

@app.route('/login', methods=['GET', 'POST'])
def login():
    from flask_login import login_user, current_user
    from models import User
    if current_user.is_authenticated:
        return redirect(url_for('admin'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip().lower()
        password = request.form.get('password', '')
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user, remember=True)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('admin'))
        flash('Invalid username or password.', 'error')
    return render_template('login.html')


@app.route('/logout')
def logout():
    from flask_login import logout_user
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))


# ── ENTRY POINT ───────────────────────────────────────────────────────────────

if __name__ == '__main__':
    app.run(debug=os.getenv('FLASK_DEBUG', 'false').lower() == 'true')
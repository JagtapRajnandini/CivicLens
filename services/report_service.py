import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app
from models import db, Report
from services import ai_service


def allowed_file(filename: str) -> bool:
    """Check file extension against allowed set."""
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in current_app.config['ALLOWED_EXTENSIONS']


def save_image(file) -> str:
    """
    Save uploaded file with a UUID filename to prevent collisions.
    Returns the path relative to the static folder for use in templates.
    Raises ValueError if file type is not allowed.
    """
    if not allowed_file(file.filename):
        raise ValueError(
            f"File type not allowed. Accepted: "
            f"{', '.join(current_app.config['ALLOWED_EXTENSIONS'])}"
        )
    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"
    upload_folder = current_app.config['UPLOAD_FOLDER']
    os.makedirs(upload_folder, exist_ok=True)
    abs_path = os.path.join(upload_folder, filename)
    file.save(abs_path)
    return f"uploads/{filename}"


def get_prior_reports(location_text: str, issue_type: str, exclude_id: int = None):
    """
    Query the DB for prior reports at the same location with the same issue type.
    Uses case-insensitive keyword matching on location_text.
    Returns a list of Report objects.
    """
    location_keyword = (
        location_text.split(',')[0].strip()
        if ',' in location_text
        else location_text[:30]
    )

    query = Report.query.filter(
        Report.location_text.ilike(f'%{location_keyword}%'),
        Report.issue_type == issue_type,
    )
    if exclude_id:
        query = query.filter(Report.id != exclude_id)

    return query.order_by(Report.created_at.desc()).limit(10).all()


def process_report_submission(form_data: dict, image_file) -> Report:
    """
    Full submission pipeline:
      1. Save image to disk
      2. Gemini Role 1+2: vision analysis + impact scoring
      3. Query DB for prior reports at same location / issue type
      4. Gemini Role 3: recurrence analysis (only if prior reports exist)
      5. Save report to DB and flush → get DB-assigned auto-increment ID
      6. Derive tracking_id from report.id (eliminates race condition)
      7. Gemini Role 4: escalation letter (now that tracking_id is known)
      8. Commit and return

    Raises ValueError on invalid image type.
    Gemini failures fall back to safe defaults inside ai_service — never raise here.
    """
    # 1. Save image
    relative_image_path = save_image(image_file)
    abs_image_path = os.path.join(
        current_app.config['BASE_DIR'], 'static', relative_image_path
    )

    # 2. Vision analysis
    analysis = ai_service.analyze_image(
        image_path=abs_image_path,
        location_text=form_data['location_text'],
        area_type=form_data['area_type'],
    )

    # 3. Recurrence check
    prior_reports = get_prior_reports(
        location_text=form_data['location_text'],
        issue_type=analysis['issue_type'],
    )

    # 4. Recurrence analysis
    recurrence_data = {
        'is_recurring': False,
        'recurrence_count': 0,
        'recurrence_pattern': None,
        'escalation_level': 'standard',
    }
    if prior_reports:
        recurrence_input = {
            'issue_type': analysis['issue_type'],
            'location_text': form_data['location_text'],
            'severity': analysis['severity'],
            'description': analysis['description'],
        }
        recurrence_data = ai_service.analyze_recurrence(recurrence_input, prior_reports)

    # Parse optional coordinates
    try:
        lat = float(form_data['latitude']) if form_data.get('latitude') else None
        lng = float(form_data['longitude']) if form_data.get('longitude') else None
    except ValueError:
        lat = None
        lng = None

    # 5. Insert with placeholder tracking_id; flush to get DB-assigned id
    report = Report(
        tracking_id='PENDING',
        image_path=relative_image_path,
        location_text=form_data['location_text'],
        area_type=form_data['area_type'],
        issue_type=analysis['issue_type'],
        severity=analysis['severity'],
        description=analysis['description'],
        department=analysis['department'],
        department_reasoning=analysis['department_reasoning'],
        impact_score=analysis['impact_score'],
        impact_reasoning=analysis['impact_reasoning'],
        confidence_score=analysis['confidence_score'],
        is_recurring=recurrence_data['is_recurring'],
        recurrence_count=recurrence_data['recurrence_count'],
        recurrence_pattern=recurrence_data['recurrence_pattern'],
        escalation_level=recurrence_data['escalation_level'],
        escalation_letter='',
        status='reported',
        latitude=lat,
        longitude=lng,
    )
    db.session.add(report)
    db.session.flush()  # Assigns report.id — no commit yet

    # 6. Derive tracking_id from the guaranteed-unique auto-increment ID
    report.tracking_id = f"CL-{report.id:04d}"

    # 7. Generate escalation letter with the real tracking_id
    class _TempReport:
        pass

    temp = _TempReport()
    temp.tracking_id = report.tracking_id
    temp.issue_type = analysis['issue_type']
    temp.location_text = form_data['location_text']
    temp.area_type = form_data['area_type']
    temp.severity = analysis['severity']
    temp.description = analysis['description']
    temp.department = analysis['department']
    temp.impact_score = analysis['impact_score']
    temp.impact_reasoning = analysis['impact_reasoning']
    temp.is_recurring = recurrence_data['is_recurring']
    temp.recurrence_count = recurrence_data['recurrence_count']
    temp.recurrence_pattern = recurrence_data['recurrence_pattern']
    temp.escalation_level = recurrence_data['escalation_level']

    report.escalation_letter = ai_service.generate_escalation_letter(temp)

    # 8. Commit everything atomically
    db.session.commit()
    return report
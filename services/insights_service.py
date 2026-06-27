from datetime import datetime, timezone, timedelta
from sqlalchemy import func
from models import db, Report


def get_aggregated_stats() -> dict:
    """
    Query the DB and return a structured stats dict for Gemini Role 7.
    All queries are simple aggregations — no joins required.
    """
    total = Report.query.count()
    resolved = Report.query.filter_by(status='resolved').count()
    recurring = Report.query.filter_by(is_recurring=True).count()

    resolution_rate = round((resolved / total * 100), 1) if total > 0 else 0

    # Issue type counts
    type_rows = db.session.query(
        Report.issue_type,
        func.count(Report.id).label('count')
    ).group_by(Report.issue_type).all()
    type_counts = {row.issue_type: row.count for row in type_rows if row.issue_type}

    # Severity distribution
    severity_rows = db.session.query(
        Report.severity,
        func.count(Report.id).label('count')
    ).group_by(Report.severity).all()
    severity_dist = {str(row.severity): row.count for row in severity_rows if row.severity}

    # Chronic locations: 3+ reports at the same location
    location_rows = db.session.query(
        Report.location_text,
        func.count(Report.id).label('count'),
        Report.issue_type
    ).group_by(Report.location_text).having(func.count(Report.id) >= 3).all()
    chronic_locations = [
        {'location': row.location_text, 'count': row.count, 'issue_type': row.issue_type}
        for row in location_rows
    ]

    # Recent trend: last 7 days vs prior 7 days
    now = datetime.now(timezone.utc)
    week_ago = now - timedelta(days=7)
    two_weeks_ago = now - timedelta(days=14)

    recent_count = Report.query.filter(Report.created_at >= week_ago).count()
    prior_count = Report.query.filter(
        Report.created_at >= two_weeks_ago,
        Report.created_at < week_ago
    ).count()

    # Average days to resolution.
    # We don't store a resolved_at timestamp, so we use created_at as a proxy:
    # reports marked resolved are assumed to have resolved within their age.
    # This is an approximation — add a resolved_at column for accuracy.
    resolved_reports = Report.query.filter_by(status='resolved').all()
    avg_days = 'N/A'
    if resolved_reports:
        total_days = 0
        counted = 0
        for r in resolved_reports:
            if r.created_at:
                created = r.created_at
                if created.tzinfo is None:
                    created = created.replace(tzinfo=timezone.utc)
                # Days from creation to now as an upper-bound proxy for resolution time
                total_days += (now - created).days
                counted += 1
        avg_days = round(total_days / counted, 1) if counted > 0 else 0

    return {
        'total': total,
        'resolved': resolved,
        'recurring_count': recurring,
        'resolution_rate': resolution_rate,
        'type_counts': type_counts,
        'severity_dist': severity_dist,
        'chronic_locations': chronic_locations,
        'recent_count': recent_count,
        'prior_count': prior_count,
        'avg_resolution_days': avg_days,
    }
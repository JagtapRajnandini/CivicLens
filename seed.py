"""
Run this script ONCE on Render after final deployment to populate demo data.

Usage:
  Local:  python seed.py
  Render: Run via Render Shell tab, or as a one-time job.

WARNING: Running this multiple times will create duplicate records.
Check the DB first: python -c "from main import app; from models import Report; 
  app.app_context().push(); print(Report.query.count(), 'reports')"
"""
import os
import sys
from datetime import datetime, timezone, timedelta

# Ensure the app can be imported
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('GEMINI_API_KEY', 'seed-placeholder')
os.environ.setdefault('SECRET_KEY', 'seed-placeholder')

from main import app
from models import db, Report


SEED_REPORTS = [
    {
        'tracking_id': 'CL-0001',
        'image_path': 'uploads/placeholder.jpg',
        'location_text': 'MG Road, near SBI ATM, Solapur',
        'area_type': 'main_road',
        'issue_type': 'Pothole',
        'severity': 4,
        'description': 'Large structural pothole approximately 60cm diameter on the main road surface. Significant subsurface depression visible causing vehicle swerving.',
        'department': 'PWD (Roads)',
        'department_reasoning': 'Road maintenance and repair falls under the Public Works Department.',
        'impact_score': 8,
        'impact_reasoning': 'Located on a primary commuter route with 2000+ daily users. Proximity to school zone increases risk during peak hours.',
        'confidence_score': 0.92,
        'is_recurring': True,
        'recurrence_count': 3,
        'recurrence_pattern': 'This location has had 3 pothole reports in the last 45 days. Pattern is consistent with temporary patching without structural repair. Each report follows within 14 days of a prior "resolved" status.',
        'escalation_level': 'urgent',
        'status': 'in_progress',
        'escalation_letter': 'Date: [Date of Filing]\n\nTo,\nThe PWD (Roads),\nMunicipal Corporation\n\nSubject: Urgent Complaint — Recurring Pothole at MG Road [CivicLens ID: CL-0001]\n\nDear Sir/Madam,\n\nI wish to formally bring to your attention a severe pothole at MG Road, near SBI ATM, Solapur. The issue has been documented as a large structural depression of approximately 60cm diameter causing significant hazard to commuters.\n\nThis location serves over 2,000 daily users and poses particular risk near the school zone during peak hours. I demand immediate inspection and permanent structural repair within 14 days. Failure to respond within 30 days will result in a formal RTI filing.\n\nYours sincerely,\n[Your Full Name]\n[Your Address]\n\nReference: CivicLens Tracking ID: CL-0001',
        'escalation_due': True,
        'latitude': 17.6868,
        'longitude': 75.9100,
        'days_old': 5,
    },
    {
        'tracking_id': 'CL-0002',
        'image_path': 'uploads/placeholder.jpg',
        'location_text': 'Station Road, opposite Bus Stand, Solapur',
        'area_type': 'commercial',
        'issue_type': 'Broken Streetlight',
        'severity': 3,
        'description': 'Two consecutive streetlights non-functional on Station Road. Area remains unlit after 8pm creating safety hazard.',
        'department': 'MSEDCL / Street Lighting Dept',
        'department_reasoning': 'Street lighting maintenance is handled by the electricity distribution company or municipal lighting department.',
        'impact_score': 7,
        'impact_reasoning': 'Commercial area with high evening foot traffic. Non-functional lights increase accident and theft risk.',
        'confidence_score': 0.88,
        'is_recurring': True,
        'recurrence_count': 2,
        'recurrence_pattern': 'Second report in 30 days at this location. Previous report was marked resolved but lights are non-functional again.',
        'escalation_level': 'elevated',
        'status': 'reported',
        'escalation_letter': 'Date: [Date of Filing]\n\nTo,\nThe MSEDCL / Street Lighting Dept,\nMunicipal Corporation\n\nSubject: Complaint — Broken Streetlight at Station Road [CivicLens ID: CL-0002]\n\nDear Sir/Madam,\n\nTwo consecutive streetlights on Station Road, opposite the Bus Stand, have been non-functional for an extended period. This creates a public safety hazard in a high-traffic commercial area.\n\nImmediate repair is requested within 14 days.\n\nYours sincerely,\n[Your Full Name]\n[Your Address]\n\nReference: CivicLens Tracking ID: CL-0002',
        'escalation_due': False,
        'latitude': 17.6944,
        'longitude': 75.9064,
        'days_old': 2,
    },
    {
        'tracking_id': 'CL-0003',
        'image_path': 'uploads/placeholder.jpg',
        'location_text': 'Vijapur Road, near Water Tank, Solapur',
        'area_type': 'residential',
        'issue_type': 'Water Leakage',
        'severity': 5,
        'description': 'Major water pipeline burst causing continuous leakage. Road waterlogged for 20-metre stretch. Water supply interrupted to nearby households.',
        'department': 'Water Supply Department',
        'department_reasoning': 'Pipeline maintenance and water supply is under the municipal Water Supply and Sewerage Board.',
        'impact_score': 9,
        'impact_reasoning': 'Affects water supply to approximately 150 households. Road damage from waterlogging is accelerating.',
        'confidence_score': 0.95,
        'is_recurring': False,
        'recurrence_count': 0,
        'recurrence_pattern': None,
        'escalation_level': 'standard',
        'status': 'reported',
        'escalation_letter': 'Date: [Date of Filing]\n\nTo,\nThe Water Supply Department,\nMunicipal Corporation\n\nSubject: URGENT — Water Pipeline Burst at Vijapur Road [CivicLens ID: CL-0003]\n\nDear Sir/Madam,\n\nA major water pipeline has burst near the Water Tank on Vijapur Road, causing continuous leakage and road waterlogging over a 20-metre stretch. Approximately 150 households face interrupted water supply.\n\nThis is a critical infrastructure failure requiring emergency attention within 48 hours.\n\nYours sincerely,\n[Your Full Name]\n[Your Address]\n\nReference: CivicLens Tracking ID: CL-0003',
        'escalation_due': False,
        'latitude': 17.7027,
        'longitude': 75.9217,
        'days_old': 1,
    },
    {
        'tracking_id': 'CL-0004',
        'image_path': 'uploads/placeholder.jpg',
        'location_text': 'Hotgi Road, near School No. 5, Solapur',
        'area_type': 'school_zone',
        'issue_type': 'Damaged Footpath',
        'severity': 3,
        'description': 'Footpath tiles broken and displaced across 15-metre stretch near school entrance. Exposed edges and gaps visible.',
        'department': 'Municipal Roads Department',
        'department_reasoning': 'Footpath construction and repair is the responsibility of the municipal roads department.',
        'impact_score': 7,
        'impact_reasoning': 'School zone with high child pedestrian traffic. Displaced tiles create trip hazard particularly for children.',
        'confidence_score': 0.83,
        'is_recurring': False,
        'recurrence_count': 0,
        'recurrence_pattern': None,
        'escalation_level': 'standard',
        'status': 'resolved',
        'escalation_letter': 'Date: [Date of Filing]\n\nTo,\nThe Municipal Roads Department,\nMunicipal Corporation\n\nSubject: Complaint — Damaged Footpath near School [CivicLens ID: CL-0004]\n\nDear Sir/Madam,\n\nThe footpath near School No. 5 on Hotgi Road has significant tile displacement across 15 metres. This poses a trip hazard for schoolchildren.\n\nPlease arrange repair within 14 days.\n\nYours sincerely,\n[Your Full Name]\n[Your Address]\n\nReference: CivicLens Tracking ID: CL-0004',
        'escalation_due': False,
        'latitude': 17.6783,
        'longitude': 75.9312,
        'days_old': 10,
    },
    {
        'tracking_id': 'CL-0005',
        'image_path': 'uploads/placeholder.jpg',
        'location_text': 'MG Road, near SBI ATM, Solapur',
        'area_type': 'main_road',
        'issue_type': 'Pothole',
        'severity': 3,
        'description': 'Medium pothole repaired but filling already cracking after 10 days. Road surface shows signs of subsidence.',
        'department': 'PWD (Roads)',
        'department_reasoning': 'Road surface repair is the responsibility of the Public Works Department.',
        'impact_score': 6,
        'impact_reasoning': 'Same main road location as prior reports. Temporary repair already failing.',
        'confidence_score': 0.79,
        'is_recurring': True,
        'recurrence_count': 2,
        'recurrence_pattern': 'Second report at this exact location within 20 days of previous repair. Consistent with shallow patching over structural damage.',
        'escalation_level': 'elevated',
        'status': 'in_progress',
        'escalation_letter': 'Date: [Date of Filing]\n\nTo,\nThe PWD (Roads),\nMunicipal Corporation\n\nSubject: Complaint — Recurring Pothole MG Road [CivicLens ID: CL-0005]\n\nA previously reported pothole at MG Road has recurred within 10 days of temporary repair. Structural repair is required.\n\nYours sincerely,\n[Your Full Name]\n\nReference: CL-0005',
        'escalation_due': False,
        'latitude': 17.6870,
        'longitude': 75.9103,
        'days_old': 4,
    },
    {
        'tracking_id': 'CL-0006',
        'image_path': 'uploads/placeholder.jpg',
        'location_text': 'Akkalkot Road, opposite Market Yard, Solapur',
        'area_type': 'commercial',
        'issue_type': 'Waste Dumping',
        'severity': 2,
        'description': 'Unauthorized waste dumping site has formed on roadside. Mixed solid and construction waste accumulating over 3-metre area.',
        'department': 'Solid Waste Management Dept',
        'department_reasoning': 'Solid waste clearance and enforcement of dumping regulations is the SWM department mandate.',
        'impact_score': 5,
        'impact_reasoning': 'Market area generates health and hygiene concerns. Fly breeding risk during summer months.',
        'confidence_score': 0.90,
        'is_recurring': False,
        'recurrence_count': 0,
        'recurrence_pattern': None,
        'escalation_level': 'standard',
        'status': 'reported',
        'escalation_letter': 'Date: [Date of Filing]\n\nTo,\nThe Solid Waste Management Dept,\nMunicipal Corporation\n\nSubject: Complaint — Unauthorized Waste Dumping [CivicLens ID: CL-0006]\n\nUnauthorized waste accumulation on Akkalkot Road requires immediate clearance and enforcement action.\n\nYours sincerely,\n[Your Full Name]\n\nReference: CL-0006',
        'escalation_due': False,
        'latitude': 17.6724,
        'longitude': 75.8987,
        'days_old': 3,
    },
]


def run_seed():
    with app.app_context():
        existing = Report.query.count()
        if existing > 0:
            print(f'Database already has {existing} reports. Skipping seed to avoid duplicates.')
            print('To force re-seed, delete instance/civiclens.db first.')
            return

        now = datetime.now(timezone.utc)

        for data in SEED_REPORTS:
            days_old = data.pop('days_old', 0)
            created_at = now - timedelta(days=days_old)

            report = Report(
                created_at=created_at,
                **{k: v for k, v in data.items()}
            )
            db.session.add(report)

        db.session.commit()
        count = Report.query.count()
        print(f'Seeded {count} reports successfully.')
        print('Run the app and visit /feed, /admin, /map, /insights to verify.')


if __name__ == '__main__':
    run_seed()
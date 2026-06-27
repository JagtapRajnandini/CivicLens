"""
CivicLens demo data seeder.

Run ONCE after deploying to populate the database with realistic demo records.
All records include real coordinates for Solapur, Maharashtra.

Usage:
    python seed.py

WARNING: Running this on a non-empty database is safe — it checks first.
"""
import os
import sys
from datetime import datetime, timezone, timedelta

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
        'description': 'Large structural pothole approximately 60cm diameter on the main road surface. Significant subsurface depression visible causing vehicles to swerve. Road surface cracking extends outward for additional 30cm.',
        'department': 'PWD (Roads)',
        'department_reasoning': 'Road surface maintenance and repair falls under the Public Works Department.',
        'impact_score': 8,
        'impact_reasoning': 'Located on a primary commuter route serving 2,000+ daily users. Proximity to school zone increases pedestrian risk during peak hours.',
        'confidence_score': 0.92,
        'is_recurring': True,
        'recurrence_count': 3,
        'recurrence_pattern': 'This location has had 3 pothole reports in the last 45 days. Pattern is consistent with repeated temporary patching without structural repair. Each report follows within 14 days of a prior "resolved" status update.',
        'escalation_level': 'urgent',
        'status': 'in_progress',
        'escalation_letter': 'Date: [Date of Filing]\n\nTo,\nThe PWD (Roads),\nMunicipal Corporation, Solapur\n\nSubject: Urgent Complaint — Recurring Pothole at MG Road [CivicLens ID: CL-0001]\n\nDear Sir/Madam,\n\nI wish to formally bring to your attention a severe structural pothole at MG Road, near SBI ATM, Solapur. The road surface shows a 60cm depression with outward cracking, posing immediate hazard to motorists and pedestrians.\n\nThis location serves over 2,000 daily commuters and is in proximity to a school zone, increasing risk to children during peak hours.\n\nCritically, this is the third report filed at this exact location within 45 days. Prior reports were marked "resolved" after temporary patching, but the pothole has recurred each time, indicating inadequate structural repair.\n\nI demand immediate structural inspection and permanent repair within 14 days, not another temporary patch. Failure to respond within 30 days will compel me to file a formal RTI application under the Right to Information Act 2005.\n\nYours sincerely,\n[Your Full Name]\n[Your Address]\n[Contact Number]\n\nReference: Reported via CivicLens — Tracking ID: CL-0001',
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
        'description': 'Two consecutive streetlights non-functional on Station Road. Area remains completely unlit after 8pm. Wiring appears exposed on one pole.',
        'department': 'Street Lighting Department / MSEDCL',
        'department_reasoning': 'Street lighting maintenance is handled by the electricity distribution company in coordination with the municipal lighting department.',
        'impact_score': 7,
        'impact_reasoning': 'Commercial area with high evening foot traffic near the bus stand. Non-functional lights increase accident and theft risk after dark.',
        'confidence_score': 0.88,
        'is_recurring': True,
        'recurrence_count': 2,
        'recurrence_pattern': 'Second report at this location within 30 days. Previous report was marked resolved but streetlights are non-functional again, suggesting wiring or transformer issue rather than simple bulb replacement.',
        'escalation_level': 'elevated',
        'status': 'reported',
        'escalation_letter': 'Date: [Date of Filing]\n\nTo,\nThe Street Lighting Department / MSEDCL,\nMunicipal Corporation, Solapur\n\nSubject: Complaint — Broken Streetlights at Station Road [CivicLens ID: CL-0002]\n\nDear Sir/Madam,\n\nTwo consecutive streetlights on Station Road, opposite the Bus Stand, have been non-functional, leaving the area unlit after 8pm. Exposed wiring on one pole presents an additional safety concern.\n\nThis is a high-traffic commercial zone and the repeated failure suggests a structural electrical fault.\n\nI request immediate repair within 14 days. Failure to respond within 30 days will result in RTI filing.\n\nYours sincerely,\n[Your Full Name]\n[Your Address]\n\nReference: CivicLens Tracking ID: CL-0002',
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
        'description': 'Major water pipeline burst causing continuous leakage. Road waterlogged for 20-metre stretch with water visible gushing from a pipe joint. Water supply interrupted to nearby residential area.',
        'department': 'Water Supply & Sewerage Board',
        'department_reasoning': 'Pipeline maintenance and water supply is under the municipal Water Supply and Sewerage Board.',
        'impact_score': 9,
        'impact_reasoning': 'Affects water supply to approximately 150 households. Accelerating road damage from continuous waterlogging threatens road surface stability.',
        'confidence_score': 0.95,
        'is_recurring': False,
        'recurrence_count': 0,
        'recurrence_pattern': None,
        'escalation_level': 'standard',
        'status': 'reported',
        'escalation_letter': 'Date: [Date of Filing]\n\nTo,\nThe Water Supply & Sewerage Board,\nMunicipal Corporation, Solapur\n\nSubject: URGENT — Water Pipeline Burst at Vijapur Road [CivicLens ID: CL-0003]\n\nDear Sir/Madam,\n\nA major water pipeline has burst near the Water Tank on Vijapur Road, Solapur. Continuous water leakage has waterlogged a 20-metre stretch of road and interrupted supply to approximately 150 households.\n\nThis is a critical infrastructure failure requiring emergency response within 48 hours.\n\nFailure to respond within 30 days will result in a formal RTI filing.\n\nYours sincerely,\n[Your Full Name]\n[Address]\n\nReference: CivicLens Tracking ID: CL-0003',
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
        'description': 'Footpath tiles broken and displaced across a 15-metre stretch near the school entrance. Exposed edges and 5cm gaps visible between tiles. Some tiles tilted creating trip hazards.',
        'department': 'Municipal Roads Department',
        'department_reasoning': 'Footpath construction and repair falls under the municipal roads and civil works department.',
        'impact_score': 7,
        'impact_reasoning': 'School zone with high child pedestrian traffic during morning and afternoon hours. Displaced tiles create significant trip hazards particularly for schoolchildren.',
        'confidence_score': 0.83,
        'is_recurring': False,
        'recurrence_count': 0,
        'recurrence_pattern': None,
        'escalation_level': 'standard',
        'status': 'resolved',
        'escalation_letter': 'Date: [Date of Filing]\n\nTo,\nThe Municipal Roads Department,\nMunicipal Corporation, Solapur\n\nSubject: Complaint — Damaged Footpath near School No. 5 [CivicLens ID: CL-0004]\n\nDear Sir/Madam,\n\nThe footpath near School No. 5 on Hotgi Road has significant tile displacement across 15 metres, creating trip hazards for schoolchildren.\n\nI request repair within 14 days.\n\nYours sincerely,\n[Your Full Name]\n\nReference: CivicLens Tracking ID: CL-0004',
        'escalation_due': False,
        'latitude': 17.6783,
        'longitude': 75.9312,
        'days_old': 12,
    },
    {
        'tracking_id': 'CL-0005',
        'image_path': 'uploads/placeholder.jpg',
        'location_text': 'MG Road, near SBI ATM, Solapur',
        'area_type': 'main_road',
        'issue_type': 'Pothole',
        'severity': 3,
        'description': 'Pothole repair filling already cracking after 10 days. Patched area shows subsidence and the fill material is separating from the road surface edges.',
        'department': 'PWD (Roads)',
        'department_reasoning': 'Road surface repair and maintenance falls under the Public Works Department.',
        'impact_score': 6,
        'impact_reasoning': 'Same primary commuter route as prior reports. Premature repair failure risks rapid reformation of the original hazard.',
        'confidence_score': 0.79,
        'is_recurring': True,
        'recurrence_count': 2,
        'recurrence_pattern': 'Second report at this exact location within 20 days of a previous temporary repair. Pattern is consistent with shallow bitumen patching over structural road damage without base repair.',
        'escalation_level': 'elevated',
        'status': 'in_progress',
        'escalation_letter': 'Date: [Date of Filing]\n\nTo,\nThe PWD (Roads),\nMunicipal Corporation, Solapur\n\nSubject: Complaint — Recurring Pothole MG Road [CivicLens ID: CL-0005]\n\nA pothole repair at MG Road has failed within 10 days. Structural base repair is required.\n\nYours sincerely,\n[Your Full Name]\n\nReference: CL-0005',
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
        'issue_type': 'Garbage / Waste',
        'severity': 2,
        'description': 'Unauthorized waste dumping site has formed on the roadside. Mixed household and construction waste accumulated over a 3-metre area. Plastic bags, concrete rubble, and organic waste visible.',
        'department': 'Solid Waste Management Department',
        'department_reasoning': 'Solid waste clearance and enforcement of anti-dumping regulations falls under the Solid Waste Management Department mandate.',
        'impact_score': 5,
        'impact_reasoning': 'Market area generates health and hygiene concerns. Fly and rodent breeding risk increases during summer months.',
        'confidence_score': 0.90,
        'is_recurring': False,
        'recurrence_count': 0,
        'recurrence_pattern': None,
        'escalation_level': 'standard',
        'status': 'reported',
        'escalation_letter': 'Date: [Date of Filing]\n\nTo,\nThe Solid Waste Management Department,\nMunicipal Corporation, Solapur\n\nSubject: Complaint — Unauthorized Waste Dumping at Akkalkot Road [CivicLens ID: CL-0006]\n\nUnauthorized waste accumulation on Akkalkot Road requires immediate clearance and enforcement action to prevent health hazard.\n\nYours sincerely,\n[Your Full Name]\n\nReference: CL-0006',
        'escalation_due': False,
        'latitude': 17.6724,
        'longitude': 75.8987,
        'days_old': 3,
    },
    {
        'tracking_id': 'CL-0007',
        'image_path': 'uploads/placeholder.jpg',
        'location_text': 'Pune-Solapur Highway, near Toll Plaza, Solapur',
        'area_type': 'main_road',
        'issue_type': 'Road Damage',
        'severity': 4,
        'description': 'Large section of highway surface has completely deteriorated over 40-metre stretch. Exposed aggregate, multiple potholes coalescing into a single degraded section. High-speed traffic presents severe accident risk.',
        'department': 'PWD (Roads)',
        'department_reasoning': 'State highway maintenance falls under PWD jurisdiction.',
        'impact_score': 9,
        'impact_reasoning': 'High-speed national highway with heavy truck and inter-city bus traffic. Degraded surface at highway speeds creates serious accident hazard for all vehicle types.',
        'confidence_score': 0.91,
        'is_recurring': True,
        'recurrence_count': 4,
        'recurrence_pattern': 'Four reports at this location over 60 days. Road damage is worsening progressively despite reports. Pattern indicates structural base failure of the highway surface, not isolated pothole damage. Seasonal monsoon damage may be accelerating deterioration.',
        'escalation_level': 'urgent',
        'status': 'under_review',
        'escalation_letter': 'Date: [Date of Filing]\n\nTo,\nThe PWD (Roads),\nMunicipal Corporation, Solapur\n\nSubject: URGENT — Severe Road Deterioration, Pune-Solapur Highway [CivicLens ID: CL-0007]\n\nA 40-metre section of the Pune-Solapur Highway near the Toll Plaza has severely deteriorated, creating immediate accident risk for high-speed traffic.\n\nThis is the fourth report at this location. Structural repair is urgently required.\n\nYours sincerely,\n[Your Full Name]\n\nReference: CL-0007',
        'escalation_due': True,
        'latitude': 17.7192,
        'longitude': 75.9489,
        'days_old': 6,
    },
    {
        'tracking_id': 'CL-0008',
        'image_path': 'uploads/placeholder.jpg',
        'location_text': 'Siddheshwar Temple Road, Solapur',
        'area_type': 'residential',
        'issue_type': 'Sewage Overflow',
        'severity': 4,
        'description': 'Open drain overflowing onto main pedestrian path near temple. Sewage water visible on road surface, strong odour present. Drain blockage appears to be waste accumulation.',
        'department': 'Water Supply & Sewerage Board',
        'department_reasoning': 'Sewage drain maintenance and overflow resolution falls under the Water Supply and Sewerage Board.',
        'impact_score': 8,
        'impact_reasoning': 'Temple road with high pedestrian traffic from devotees. Sewage overflow creates serious public health hazard and degrades the religious and cultural site environment.',
        'confidence_score': 0.87,
        'is_recurring': False,
        'recurrence_count': 0,
        'recurrence_pattern': None,
        'escalation_level': 'standard',
        'status': 'reported',
        'escalation_letter': 'Date: [Date of Filing]\n\nTo,\nThe Water Supply & Sewerage Board,\nMunicipal Corporation, Solapur\n\nSubject: Complaint — Sewage Overflow at Siddheshwar Temple Road [CivicLens ID: CL-0008]\n\nAn open drain overflow is contaminating the pedestrian area near Siddheshwar Temple. Immediate drain clearance is required.\n\nYours sincerely,\n[Your Full Name]\n\nReference: CL-0008',
        'escalation_due': False,
        'latitude': 17.6855,
        'longitude': 75.9041,
        'days_old': 1,
    },
]


def run_seed():
    with app.app_context():
        existing = Report.query.count()
        if existing > 0:
            print(f'Database already has {existing} reports.')
            confirm = input('Add seed data anyway? This creates duplicates. (yes/no): ').strip().lower()
            if confirm != 'yes':
                print('Aborted.')
                return

        now = datetime.now(timezone.utc)

        for data in SEED_REPORTS:
            days_old = data.pop('days_old', 0)
            created_at = now - timedelta(days=days_old)
            report = Report(created_at=created_at, **data)
            db.session.add(report)

        db.session.commit()
        count = Report.query.count()
        print(f'✓ Seeded {count} reports.')
        print('Visit /feed, /map, /admin, /insights to verify.')


if __name__ == '__main__':
    run_seed()
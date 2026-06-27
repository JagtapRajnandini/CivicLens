import json
import google.genai as genai
from google.genai import types
from flask import current_app


def _get_client():
    """Return a configured google-genai Client instance."""
    return genai.Client(api_key=current_app.config['GEMINI_API_KEY'])


def _json_config():
    """GenerateContentConfig that forces JSON response."""
    return types.GenerateContentConfig(
        response_mime_type='application/json'
    )


def analyze_image(image_path: str, location_text: str, area_type: str) -> dict:
    """
    Gemini Role 1+2: Vision analysis + community impact scoring.
    Single API call. Returns classification, severity, department,
    impact score, and confidence. Returns safe defaults on failure.
    """
    default = {
        'issue_type': 'Unknown',
        'severity': 3,
        'description': 'Unable to analyze image. Please review manually.',
        'department': 'Municipal Corporation',
        'department_reasoning': 'Default assignment pending manual review.',
        'impact_score': 5,
        'impact_reasoning': 'Impact assessment unavailable.',
        'confidence_score': 0.0,
    }
    try:
        client = _get_client()

        with open(image_path, 'rb') as f:
            image_bytes = f.read()

        # Detect MIME type from extension
        ext = image_path.rsplit('.', 1)[-1].lower()
        mime_map = {
            'jpg': 'image/jpeg', 'jpeg': 'image/jpeg',
            'png': 'image/png', 'webp': 'image/webp',
            'heic': 'image/heic',
        }
        mime_type = mime_map.get(ext, 'image/jpeg')

        image_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)

        prompt = (
            "You are CivicLens AI, a civic infrastructure analyst for Indian urban areas.\n"
            "Analyze the image and the provided context.\n\n"
            f"Location: {location_text}\n"
            f"Area type: {area_type}\n\n"
            "Return ONLY valid JSON with exactly these fields:\n"
            "{\n"
            '  "issue_type": "one of: Pothole, Broken Streetlight, Water Leakage, '
            'Damaged Footpath, Waste Dumping, Damaged Road Marking, Fallen Tree, Sewage Overflow, Other",\n'
            '  "severity": integer 1 to 5 where 1 is minor inconvenience and 5 is critical infrastructure failure,\n'
            '  "description": "2 to 3 objective sentences describing what you see in the image",\n'
            '  "department": "the responsible municipal department name",\n'
            '  "department_reasoning": "one sentence explaining why this department is responsible",\n'
            '  "impact_score": integer 1 to 10 based on how many people are affected,\n'
            '  "impact_reasoning": "2 sentences describing who is affected and estimated population impact",\n'
            '  "confidence_score": float between 0.0 and 1.0 representing your confidence\n'
            "}"
        )

        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=[prompt, image_part],
            config=_json_config(),
        )
        result = json.loads(response.text)

        return {
            'issue_type': str(result.get('issue_type', default['issue_type'])),
            'severity': int(result.get('severity', default['severity'])),
            'description': str(result.get('description', default['description'])),
            'department': str(result.get('department', default['department'])),
            'department_reasoning': str(result.get('department_reasoning', default['department_reasoning'])),
            'impact_score': int(result.get('impact_score', default['impact_score'])),
            'impact_reasoning': str(result.get('impact_reasoning', default['impact_reasoning'])),
            'confidence_score': float(result.get('confidence_score', default['confidence_score'])),
        }
    except Exception as e:
        current_app.logger.error(f'Gemini Role 1+2 error: {e}')
        return default


def analyze_recurrence(new_report: dict, prior_reports: list) -> dict:
    """
    Gemini Role 3: Recurrence pattern analysis.
    Called only when prior reports exist at the same location.
    """
    default = {
        'is_recurring': True,
        'recurrence_count': len(prior_reports),
        'recurrence_pattern': 'This location has multiple prior reports. Pattern analysis unavailable.',
        'escalation_level': 'elevated',
    }
    try:
        client = _get_client()

        prior_summary = []
        for r in prior_reports:
            prior_summary.append({
                'date': r.created_at.strftime('%Y-%m-%d') if r.created_at else 'unknown',
                'issue_type': r.issue_type,
                'severity': r.severity,
                'status': r.status,
            })

        prompt = (
            "You are CivicLens AI analyzing whether a newly reported civic issue represents a recurring problem.\n\n"
            "New report:\n"
            f"- Issue type: {new_report.get('issue_type')}\n"
            f"- Location: {new_report.get('location_text')}\n"
            f"- Severity: {new_report.get('severity')}\n"
            f"- Description: {new_report.get('description')}\n\n"
            "Prior reports at the same location with the same issue type:\n"
            f"{json.dumps(prior_summary, indent=2)}\n\n"
            "Return ONLY valid JSON:\n"
            "{\n"
            '  "is_recurring": true,\n'
            f'  "recurrence_count": {len(prior_reports)},\n'
            '  "recurrence_pattern": "2 to 3 sentences analyzing the pattern. Reference specific dates and statuses.",\n'
            '  "escalation_level": "one of: standard, elevated, urgent"\n'
            "}\n\n"
            "escalation_level rules:\n"
            "- elevated: 2 to 3 prior reports\n"
            "- urgent: 4 or more prior reports, or a resolved issue that recurred within 30 days"
        )

        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=prompt,
            config=_json_config(),
        )
        result = json.loads(response.text)
        return {
            'is_recurring': bool(result.get('is_recurring', True)),
            'recurrence_count': int(result.get('recurrence_count', len(prior_reports))),
            'recurrence_pattern': str(result.get('recurrence_pattern', default['recurrence_pattern'])),
            'escalation_level': str(result.get('escalation_level', 'elevated')),
        }
    except Exception as e:
        current_app.logger.error(f'Gemini Role 3 error: {e}')
        return default


def generate_escalation_letter(report) -> str:
    """
    Gemini Role 4: Formal RTI-compatible grievance letter.
    """
    try:
        client = _get_client()

        recurrence_context = ''
        if report.is_recurring:
            recurrence_context = (
                f"\nThis issue has been reported {report.recurrence_count} times previously.\n"
                f"Pattern: {report.recurrence_pattern}\n"
                f"Escalation level: {report.escalation_level}"
            )

        prompt = (
            "You are drafting a formal civic grievance letter for an Indian citizen.\n"
            "The letter must be suitable for a Municipal Corporation or PWD.\n"
            "Use formal, RTI-compatible language. Be firm but professional.\n\n"
            "Report details:\n"
            f"- Tracking ID: {report.tracking_id}\n"
            f"- Issue Type: {report.issue_type}\n"
            f"- Location: {report.location_text}\n"
            f"- Area Type: {report.area_type}\n"
            f"- Severity: {report.severity}/5\n"
            f"- Description: {report.description}\n"
            f"- Responsible Department: {report.department}\n"
            f"- Community Impact Score: {report.impact_score}/10\n"
            f"- Impact: {report.impact_reasoning}\n"
            f"{recurrence_context}\n\n"
            "Write the complete letter with:\n"
            '1. Date line: "Date: [Date of Filing]"\n'
            f'2. Recipient: "To, The {report.department}, Municipal Corporation"\n'
            "3. Subject line with issue type and tracking ID\n"
            "4. Body paragraph 1: What was observed\n"
            "5. Body paragraph 2: Community impact\n"
            "6. If recurring: History of failed resolutions\n"
            "7. Demand for resolution within 14 days\n"
            "8. RTI clause: formal RTI will be filed if no response in 30 days\n"
            '9. Closing: "Yours sincerely, [Your Full Name], [Address], [Contact]"\n'
            f"10. Reference: CivicLens Tracking ID: {report.tracking_id}\n\n"
            "Return plain text only. No markdown. No asterisks."
        )

        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=prompt,
        )
        return response.text.strip()
    except Exception as e:
        current_app.logger.error(f'Gemini Role 4 error: {e}')
        return (
            f"Date: [Date of Filing]\n\nTo,\nThe {report.department},\nMunicipal Corporation\n\n"
            f"Subject: Complaint — {report.issue_type} at {report.location_text} [{report.tracking_id}]\n\n"
            f"Dear Sir/Madam,\n\n{report.description}\n\n"
            f"I request resolution within 14 days. Non-response within 30 days will result in RTI filing.\n\n"
            f"Yours sincerely,\n[Your Full Name]\n[Address]\n\n"
            f"Reference: CivicLens Tracking ID: {report.tracking_id}"
        )


def generate_followup_letter(report) -> str:
    """
    Gemini Role 5: Autonomous follow-up escalation letter.
    Triggered automatically for stale In Progress reports.
    """
    try:
        client = _get_client()

        from datetime import datetime, timezone
        days_elapsed = 0
        if report.created_at:
            now = datetime.now(timezone.utc)
            created = report.created_at
            if created.tzinfo is None:
                created = created.replace(tzinfo=timezone.utc)
            days_elapsed = (now - created).days

        rti_clause = (
            "Reference RTI Act 2005, Section 7 — right to receive information within 30 days."
            if days_elapsed > 14
            else "Failure to respond will result in a formal RTI filing."
        )

        filed_date = report.created_at.strftime('%d %B %Y') if report.created_at else 'earlier'

        prompt = (
            "Draft an escalated follow-up complaint letter for an unresolved civic issue.\n"
            f"The original complaint was filed {days_elapsed} days ago and remains unresolved.\n"
            "Tone: firm, assertive, legally informed.\n\n"
            f"- Tracking ID: {report.tracking_id}\n"
            f"- Issue: {report.issue_type} at {report.location_text}\n"
            f"- Department: {report.department}\n"
            f"- Filed on: {filed_date}\n"
            f"- Current status: {report.status}\n\n"
            "Letter must include:\n"
            "1. Date line\n"
            f"2. To: The {report.department}, Municipal Corporation\n"
            f'3. Subject: "FOLLOW-UP: Unresolved — {report.issue_type} [{report.tracking_id}]"\n'
            "4. Reference to original complaint\n"
            f"5. Statement that {days_elapsed} days have passed without resolution\n"
            "6. Demand response within 7 days\n"
            f"7. {rti_clause}\n"
            "8. Notice of escalation to higher authorities\n"
            "9. Closing with citizen placeholder\n\n"
            "Return plain text only. No markdown."
        )

        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=prompt,
        )
        return response.text.strip()
    except Exception as e:
        current_app.logger.error(f'Gemini Role 5 error: {e}')
        return (
            f"Date: [Current Date]\n\nTo,\nThe {report.department},\nMunicipal Corporation\n\n"
            f"Subject: FOLLOW-UP — {report.issue_type} [{report.tracking_id}]\n\n"
            f"This is a follow-up to my complaint filed on "
            f"{report.created_at.strftime('%d %B %Y') if report.created_at else 'earlier'}. "
            f"The issue remains unresolved. I demand response within 7 days.\n\n"
            f"Yours sincerely,\n[Your Full Name]\n[Address]"
        )


def chat_with_assistant(report, conversation_history: list, user_message: str) -> str:
    """
    Gemini Role 6: Issue-scoped citizen AI assistant.
    """
    try:
        client = _get_client()

        history_text = ''
        for msg in conversation_history[-6:]:
            label = 'Citizen' if msg['role'] == 'user' else 'Assistant'
            history_text += f"{label}: {msg['content']}\n"

        recurring_text = (
            f"Yes — {report.recurrence_count} prior reports"
            if report.is_recurring else "No"
        )

        prompt = (
            "You are CivicLens Assistant. Help the citizen with their civic complaint.\n"
            "Be direct and specific. Keep response under 120 words.\n\n"
            "Their report:\n"
            f"- ID: {report.tracking_id}\n"
            f"- Issue: {report.issue_type} at {report.location_text}\n"
            f"- Severity: {report.severity}/5\n"
            f"- Department: {report.department}\n"
            f"- Status: {report.status}\n"
            f"- Recurring: {recurring_text}\n"
            f"- Impact: {report.impact_score}/10\n\n"
        )
        if history_text:
            prompt += f"Previous conversation:\n{history_text}\n"
        prompt += f"Citizen question: {user_message}\n\nAnswer directly."

        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=prompt,
        )
        return response.text.strip()
    except Exception as e:
        current_app.logger.error(f'Gemini Role 6 error: {e}')
        return (
            f"Unable to process your question right now. "
            f"Reference your tracking ID {report.tracking_id} when contacting the Municipal Corporation."
        )


def generate_civic_insights(stats: dict) -> dict:
    """
    Gemini Role 7: Civic health analysis for admin insights page.
    """
    default = {
        'civic_health_score': 50,
        'top_issues': [],
        'chronic_zones': [],
        'resolution_analysis': 'Insufficient data for analysis.',
        'recommendations': ['Collect more data to enable meaningful analysis.'],
    }
    try:
        client = _get_client()

        prompt = (
            "You are a civic analytics AI. Analyze this community's issue data.\n\n"
            f"- Total reports: {stats.get('total', 0)}\n"
            f"- Issue types: {json.dumps(stats.get('type_counts', {}))}\n"
            f"- Severity distribution: {json.dumps(stats.get('severity_dist', {}))}\n"
            f"- Resolution rate: {stats.get('resolution_rate', 0)}%\n"
            f"- Recurring issues: {stats.get('recurring_count', 0)}\n"
            f"- Chronic locations: {json.dumps(stats.get('chronic_locations', []))}\n"
            f"- Avg days to resolution: {stats.get('avg_resolution_days', 'N/A')}\n"
            f"- Last 7 days vs prior 7 days: {stats.get('recent_count', 0)} vs {stats.get('prior_count', 0)}\n\n"
            "Return ONLY valid JSON:\n"
            "{\n"
            '  "civic_health_score": integer 0-100,\n'
            '  "top_issues": [{"type": "name", "count": number, "avg_severity": decimal}],\n'
            '  "chronic_zones": [{"location": "text", "report_count": number, "primary_issue": "type"}],\n'
            '  "resolution_analysis": "2-3 sentence analysis",\n'
            '  "recommendations": ["action 1", "action 2", "action 3"]\n'
            "}\n\n"
            "Scoring: start 100, -2 per unresolved, -5 per chronic zone, +3 per resolved, min 0."
        )

        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=prompt,
            config=_json_config(),
        )
        result = json.loads(response.text)
        return {
            'civic_health_score': int(result.get('civic_health_score', 50)),
            'top_issues': result.get('top_issues', []),
            'chronic_zones': result.get('chronic_zones', []),
            'resolution_analysis': str(result.get('resolution_analysis', default['resolution_analysis'])),
            'recommendations': result.get('recommendations', default['recommendations']),
        }
    except Exception as e:
        current_app.logger.error(f'Gemini Role 7 error: {e}')
        return default
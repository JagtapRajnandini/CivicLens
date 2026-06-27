# CivicLens

AI-powered civic issue reporting and accountability for Indian urban communities.

## What it does

Citizens upload a photo of a civic problem — pothole, broken streetlight, water leak, waste dumping, and more.

**CivicLens AI (Google Gemini 1.5 Flash) then:**
- Classifies the issue type and assigns it to the responsible municipal department
- Scores community impact (1–10) based on affected population
- Cross-references the database to detect recurring problems at the same location
- Generates a formal **RTI-compatible grievance letter** ready to send to the department
- Provides a **Citizen AI Assistant** to answer questions about the report and next steps
- Auto-generates **follow-up escalation letters** for stale unresolved issues
- Produces **Civic Health Analytics** — health score, chronic zones, top issues, recommendations

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Flask 3.0.3, Python 3.12.3 |
| Database | SQLite (Flask-SQLAlchemy 3.1.1) |
| AI | Google Gemini 1.5 Flash (google-genai 2.10.0) — 7 roles |
| Maps | Leaflet.js 1.9.4 / OpenStreetMap |
| Deployment | Render (gunicorn) |

## Local Setup

```bash
git clone <your-repo-url>
cd CivicLens
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env — set GEMINI_API_KEY and SECRET_KEY
python seed.py                  # Populate demo data (run once)
python main.py                  # Start development server
```

Open http://localhost:5000

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `GEMINI_API_KEY` | ✅ Yes | Google AI Studio API key — get one at https://aistudio.google.com/app/apikey |
| `SECRET_KEY` | ✅ Yes | Flask session secret — generate with `python -c "import secrets; print(secrets.token_hex(32))"` |

## Deployment on Render

1. Push this repository to GitHub
2. Create a new **Web Service** on Render → connect the GitHub repo
3. Set environment variables: `GEMINI_API_KEY`, `SECRET_KEY`
4. **Build command:** `pip install -r requirements.txt`
5. **Start command:** `gunicorn main:app -w 1 --timeout 120`
6. After first deploy → open Render Shell and run: `python seed.py`

## Key Routes

| Route | Description |
|---|---|
| `/` | Home — live stats and recent reports |
| `/report` | Submit a new civic issue |
| `/confirmation/<id>` | Post-submission results, AI analysis, escalation letter, chat |
| `/feed` | Community feed — sortable by recurring / impact / recent / unresolved |
| `/issue/<id>` | Full issue detail — status timeline, letters, AI chat |
| `/map` | Geographic map of all pinned reports |
| `/insights` | AI civic health report (cached 10 min) |
| `/admin` | Admin dashboard — status management, follow-up generation |

## Demo Data

Run `python seed.py` once after setup to populate 6 realistic civic reports for the Solapur area, covering all issue types, severity levels, and escalation states.

To re-seed from scratch: delete `instance/civiclens.db`, then run `seed.py` again.

## AI Roles (Gemini 1.5 Flash)

| Role | When triggered | Purpose |
|---|---|---|
| 1+2 | Every submission | Vision analysis + impact scoring |
| 3 | Submission (if prior reports exist) | Recurrence pattern detection |
| 4 | Every submission | RTI escalation letter |
| 5 | Admin "Generate Follow-Up" button | Autonomous follow-up letter for stale issues |
| 6 | Chat messages | Citizen Q&A assistant |
| 7 | `/insights` page (cached 10 min) | Civic health analytics |
# CivicLens

**AI-powered civic issue reporting, tracking, and accountability for Indian urban communities.**

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0.3-green.svg)](https://flask.palletsprojects.com)
[![Gemini](https://img.shields.io/badge/Google%20Gemini-2.0%20Flash%20Lite-orange.svg)](https://ai.google.dev)
[![License](https://img.shields.io/badge/License-MIT-lightgrey.svg)](LICENSE)

---

## Hackathon Information

| Field | Detail |
|---|---|
| **Competition** | Coding Ninjas × Google for Developers — Vibe2Ship 2026 |
| **Problem Statement** | PS2 — Community Hero: Hyperlocal Problem Solver |
| **Participant** | Rajnandini Jagtap |

---

## Live Demo

| | |
|---|---|
| **Deployed URL** | https://civiclens-l853.onrender.com |
| **Admin Login** | https://civiclens-l853.onrender.com/login |
| **Username** | `admin` |
| **Password** | `CivicLens@2026` |

> The app is hosted on Render's free tier. If the page takes 30–50 seconds to load on first visit, this is normal — Render spins down free services after inactivity. Wait for the page to fully load before interacting.

Citizens do not need to log in. All report submission, feed, map, and insights features are publicly accessible.

---

## Elevator Pitch

CivicLens transforms a citizen's photo into a formally documented, tracked, and escalation-ready civic complaint — in under 30 seconds. The AI agent classifies the issue, detects whether it is a recurring problem at the same location, scores its community impact, generates an RTI-compatible grievance letter, and provides a citizen assistant for follow-up guidance. Administrators get an analytics dashboard with AI-generated civic health insights. No government API integration is required — impact is delivered through the document itself.

---

## Problem Statement

Indian citizens face a fragmented, opaque, and unresponsive civic reporting ecosystem:

- Reporting channels (WhatsApp groups, social media) produce no official record.
- Existing portals require manual categorization, department knowledge, and follow-through.
- Chronic problems at the same location are treated as new issues every time.
- Citizens have no usable output from the complaint process — no letter, no tracking, no escalation path.

The result: infrastructure problems go unresolved, accountability is absent, and community frustration compounds.

---

## Solution

CivicLens is a civic AI agent — not a form, not a chatbot, not a reporting portal.

A citizen uploads one photo. CivicLens autonomously:

1. **Identifies** the civic issue type using Gemini Vision
2. **Scores** community impact based on location context
3. **Detects recurrence** — whether this location has prior reports of the same problem
4. **Routes** the report to the correct municipal department with reasoning
5. **Generates** a formal RTI-compatible grievance letter ready to send
6. **Escalates** stale unresolved issues by generating follow-up letters
7. **Answers questions** about the report via a citizen AI assistant
8. **Analyzes** aggregate data into a civic health score with actionable recommendations

---

## Key Features

### Citizen Workflow

| Feature | Description |
|---|---|
| **Photo-based reporting** | Upload a photo (JPG, PNG, WEBP, HEIC up to 16 MB) — no manual categorization required |
| **Auto GPS coordinates** | Browser geolocation auto-populates coordinates on page load; manual entry available as fallback |
| **AI issue classification** | Gemini Vision identifies issue type from 10 supported categories |
| **Community impact scoring** | AI scores impact 1–10 based on location type, proximity to schools/hospitals, and area type |
| **Tracking ID** | Each report receives a unique `CL-XXXX` tracking ID |
| **Escalation letter** | Formal RTI-compatible grievance letter generated instantly and downloadable as `.txt` |
| **Citizen AI assistant** | Chat with Gemini to ask questions about the report, department contacts, and next steps |
| **Community feed** | Browse all reports sorted by recurrence, impact, recency, or unresolved status |
| **Issue map** | Leaflet.js map with severity-coded pins for all geotagged reports |
| **Status tracking** | Issues move through: Reported → Under Review → In Progress → Resolved |

### Agentic Behaviors

| Behavior | Trigger | What Happens |
|---|---|---|
| **Recurrence detection** | Every new submission | Agent queries DB for prior reports at the same location and issue type; if found, calls Gemini for pattern analysis and adjusts escalation level (standard / elevated / urgent) |
| **Follow-up escalation** | Admin trigger | Agent identifies In Progress reports older than 3 days with no follow-up letter; generates an escalated letter with RTI Act 2005 Section 7 references |
| **Civic health insights** | `/insights` page | Agent aggregates all report data and generates a civic health score (0–100), chronic zone identification, and 3 actionable municipal recommendations |

### Administrator Workflow

| Feature | Description |
|---|---|
| **Secure login** | Username/password authentication via Flask-Login with bcrypt hashing |
| **Status management** | Update any report status with one click |
| **Escalation dashboard** | View reports flagged as escalation-due, download follow-up letters |
| **Follow-up generation** | Trigger AI follow-up letter generation for stale In Progress reports |
| **Insights refresh** | Force regeneration of the cached civic health analysis |
| **Summary statistics** | Total reports, pending, in-progress, recurring, escalation-due counts |

---

## AI Integration — 7 Gemini Roles

CivicLens uses **Google Gemini 2.0 Flash Lite** via the `google-genai` Python SDK across 7 distinct roles:

| Role | Trigger | Purpose |
|---|---|---|
| **1+2 — Vision + Impact** | Every report submission | Analyzes image → classifies issue type (10 categories), severity (1–5), department assignment with reasoning, community impact score (1–10), confidence score |
| **3 — Recurrence Analysis** | When prior reports exist at the same location | Identifies pattern (temporary patching, structural failure, seasonal), sets escalation level |
| **4 — Escalation Letter** | Every report submission | Generates formal RTI-compatible grievance letter in plain text, tailored to issue type, department, and recurrence history |
| **5 — Follow-Up Letter** | Admin "Generate Follow-Up" action | Generates escalated follow-up letter for unresolved issues, with RTI Act 2005 Section 7 references if elapsed > 14 days |
| **6 — Citizen Assistant** | User chat messages on report pages | Answers citizen questions in context of their specific report (department contact, escalation steps, RTI process) |
| **7 — Civic Insights** | `/insights` page (cached 10 min) | Produces civic health score (0–100), top issue breakdown, chronic zone identification, and 3 actionable recommendations |

### Supported Issue Categories

Pothole · Broken Streetlight · Water Leakage · Garbage / Waste · Damaged Footpath · Sewage Overflow · Fallen Tree · Road Damage · Construction Obstruction · Other

---

## Google AI Studio Integration

| Detail | Value |
|---|---|
| **API Source** | [Google AI Studio](https://aistudio.google.com/app/apikey) |
| **SDK** | `google-genai` v2.10.0 |
| **Model** | `gemini-2.0-flash-lite` (all 7 roles) |
| **Multimodal** | Image bytes sent via `types.Part.from_bytes()` with MIME type detection for vision roles |
| **Structured output** | `response_mime_type='application/json'` enforces JSON-only responses for Roles 1, 3, and 7 |
| **Error handling** | Every role returns safe defaults on API failure — requests never crash |

---

## Technology Stack

| Layer | Technology | Version |
|---|---|---|
| Language | Python | 3.12.10 |
| Web Framework | Flask | 3.0.3 |
| ORM | Flask-SQLAlchemy | 3.1.1 |
| Authentication | Flask-Login | 0.6.3 |
| AI | Google Gemini (`google-genai`) | 2.10.0 |
| Database (local) | SQLite | — |
| Database (production) | PostgreSQL via `psycopg2-binary` | — |
| Maps | Leaflet.js + OpenStreetMap | 1.9.4 |
| WSGI Server | Gunicorn | 21.2.0 |
| Hosting | Render | — |
| Frontend | Jinja2 templates, plain CSS, minimal JS | — |

---

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    BROWSER (Citizen)                    │
│  HTML/CSS/JS  ←→  Flask (Jinja2 server-side rendering) │
└──────────────────────────┬──────────────────────────────┘
                           │ HTTP
┌──────────────────────────▼──────────────────────────────┐
│                  Flask Application                       │
│                                                         │
│  Routes (main.py)                                       │
│     ↓                                                   │
│  Services                                               │
│  ├── report_service.py  ← submission pipeline           │
│  ├── ai_service.py      ← all 7 Gemini roles           │
│  └── insights_service.py ← DB aggregation              │
│     ↓                                                   │
│  Models (SQLAlchemy)                                    │
│  ├── Report (25 fields)                                 │
│  ├── ChatMessage                                        │
│  └── User                                              │
└──────┬──────────────────────────────────────┬───────────┘
       │                                      │
┌──────▼──────┐                    ┌──────────▼──────────┐
│ PostgreSQL  │                    │  Google Gemini API  │
│ (Render)    │                    │  gemini-2.0-flash-  │
│ SQLite      │                    │  lite (7 roles)     │
│ (local)     │                    └─────────────────────┘
└─────────────┘
```

---

## Submission Pipeline

```
Citizen uploads photo + location
         │
         ▼
Flask saves image → Gemini Role 1+2 (Vision + Impact Analysis)
         │
         ▼
Query DB: prior reports at same location + same issue type?
         │
    ┌────┴────┐
   Yes        No
    │          │
    ▼          ▼
Gemini Role 3   Skip recurrence
(Recurrence     escalation_level = 'standard'
 Analysis)
    │
    └────┬────┘
         │
         ▼
Gemini Role 4: Generate RTI-compatible escalation letter
         │
         ▼
Save complete report to DB → Redirect to confirmation page
         │
         ▼
Citizen sees: AI classification, impact score, recurrence flag,
              department assignment, letter download, AI chat
```

---

## Application Pages

| Page | Route | Description |
|---|---|---|
| Home | `/` | Live stats (total reports, recurring, resolved), recent 4 report cards |
| Report Issue | `/report` | Photo upload with drag-and-drop, auto GPS, area type selector — full AI analysis on submit |
| Confirmation | `/confirmation/<id>` | AI report output, severity bar, impact score, recurrence flag, letter download, AI chat |
| Community Feed | `/feed` | All reports sortable by recurring / impact / recent / unresolved |
| Issue Detail | `/issue/<id>` | Full report view, status timeline, letters, AI assistant chat |
| Map | `/map` | Leaflet map with severity-coded circle markers and popup details |
| Civic Insights | `/insights` | AI civic health score (0–100), top issues, chronic zones, recommendations |
| Admin Dashboard | `/admin` | Status update table, escalation flags, follow-up generation, summary stats |
| Login | `/login` | Admin authentication |

---

## User Roles

| Feature | Citizen (anonymous) | Administrator |
|---|---|---|
| Report a civic issue | ✅ | ✅ |
| View community feed | ✅ | ✅ |
| View issue map | ✅ | ✅ |
| View civic insights | ✅ | ✅ |
| Download escalation letter | ✅ | ✅ |
| Use AI assistant chat | ✅ | ✅ |
| Update issue status | ❌ | ✅ |
| Generate follow-up letters | ❌ | ✅ |
| Refresh insights cache | ❌ | ✅ |

Citizens do not require registration or login.

---

## Database Schema

**Three tables:**

**`reports`** — Core entity (25 columns):
- Identity: `id`, `tracking_id` (`CL-XXXX`)
- Submission: `image_path`, `location_text`, `area_type`, `latitude`, `longitude`
- AI output (Role 1+2): `issue_type`, `severity`, `description`, `department`, `department_reasoning`, `impact_score`, `impact_reasoning`, `confidence_score`
- AI output (Role 3): `is_recurring`, `recurrence_count`, `recurrence_pattern`, `escalation_level`
- Letters (Roles 4+5): `escalation_letter`, `followup_letter`, `followup_generated_at`, `escalation_due`
- Lifecycle: `status`, `created_at`

**`chat_messages`** — Stores Citizen Assistant conversation history per report.

**`users`** — Admin accounts only (`username`, `password_hash`, `is_admin`).

**Database:** SQLite locally; PostgreSQL on Render (auto-detected via `DATABASE_URL` environment variable).

---

## Folder Structure

```
CivicLens/
├── main.py                   # Flask app — all routes
├── models.py                 # SQLAlchemy models (Report, ChatMessage, User)
├── config.py                 # Configuration (DB, uploads, Gemini, Flask-Login)
├── seed.py                   # Demo data seeder (8 realistic Solapur reports)
├── create_admin.py           # Interactive admin user setup (local use)
├── create_admin_auto.py      # Non-interactive admin setup for build.sh
├── build.sh                  # Render build script (install → admin → seed)
├── Procfile                  # Gunicorn start command
├── runtime.txt               # Python 3.12.10
├── requirements.txt          # Python dependencies
├── .env.example              # Environment variable template
├── services/
│   ├── ai_service.py         # All 7 Gemini roles
│   ├── report_service.py     # Report submission pipeline
│   └── insights_service.py   # DB aggregation for Gemini Role 7
├── templates/
│   ├── base.html             # Base layout (nav, footer)
│   ├── home.html             # Home page
│   ├── report.html           # Issue submission form
│   ├── confirmation.html     # Post-submission AI results
│   ├── feed.html             # Community feed
│   ├── issue_detail.html     # Full issue view
│   ├── map.html              # Leaflet map
│   ├── insights.html         # Civic health dashboard
│   ├── admin.html            # Admin dashboard
│   └── login.html            # Admin login
├── static/
│   ├── style.css             # Design system — civic color palette, components
│   ├── map.js                # Leaflet map initialization and pin rendering
│   ├── chat.js               # Citizen AI assistant chat
│   └── uploads/              # Uploaded report images (gitignored except placeholder)
```

---

## Local Installation

### Prerequisites

- Python 3.12+
- Git

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/JagtapRajnandini/CivicLens.git
cd CivicLens

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
cp .env.example .env
# Edit .env — add your GEMINI_API_KEY and SECRET_KEY

# 5. Seed demo data (run once)
python seed.py

# 6. Create an admin account
python create_admin.py

# 7. Start the development server
python main.py
```

Open [http://localhost:5000](http://localhost:5000)

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `GEMINI_API_KEY` | ✅ Required | Google AI Studio API key — [Get one here](https://aistudio.google.com/app/apikey) |
| `SECRET_KEY` | ✅ Required | Flask session secret — generate with `python -c "import secrets; print(secrets.token_hex(32))"` |
| `DATABASE_URL` | Production only | PostgreSQL connection string — Render sets this automatically when a database is linked |
| `ADMIN_USERNAME` | Build only | Admin username for automated setup via `build.sh` (default: `admin`) |
| `ADMIN_PASSWORD` | Build only | Admin password for automated setup via `build.sh` |

See `.env.example` for the complete template.

---

## Deployment on Render

### Setup

1. Push the repository to GitHub.
2. Go to [render.com](https://render.com) → **New → PostgreSQL** — create a free database and copy the **Internal Database URL**.
3. Go to **New → Web Service** → connect the GitHub repository.
4. Configure the service:

| Setting | Value |
|---|---|
| **Runtime** | Python |
| **Build Command** | `bash build.sh` |
| **Start Command** | `gunicorn main:app -w 1 --timeout 120` |
| **Python Version** | `3.12.10` (set in `runtime.txt`) |

5. Add environment variables:

| Variable | Value |
|---|---|
| `GEMINI_API_KEY` | Your key from Google AI Studio |
| `SECRET_KEY` | A random 64-character hex string |
| `DATABASE_URL` | Internal Database URL from Render PostgreSQL |
| `ADMIN_PASSWORD` | Password for the admin account |

6. Click **Create Web Service**. The `build.sh` script installs dependencies, creates the admin account, and seeds demo data automatically — no manual shell access required.

---

## Demo Credentials

> These credentials are for the evaluation environment only.

| Field | Value |
|---|---|
| **Live URL** | https://civiclens-l853.onrender.com |
| **Admin Login** | https://civiclens-l853.onrender.com/login |
| **Username** | `admin` |
| **Password** | `CivicLens@2026` |

---

## Challenges Faced

**Gemini Vision prompt and JSON mode conflict:** The original prompt included a JSON template with angle-bracket placeholders (`"<one of the valid categories>"`). When `response_mime_type='application/json'` is active, Gemini sometimes returns the template structure literally instead of filling it in. The fix was to remove the JSON template entirely and describe each field in plain English, letting the SDK enforce JSON structure.

**`gemini-1.5-flash` deprecation on v1beta API:** During deployment, Roles 3–7 (which used `gemini-1.5-flash`) began returning 404 NOT_FOUND errors because this model was removed from the v1beta endpoint used by `google-genai` v2.x. Switching all roles to `gemini-2.0-flash-lite` resolved this.

**Free tier quota exhaustion:** The `gemini-2.0-flash` model has a stricter free-tier quota than `gemini-2.0-flash-lite`. After several test submissions during development, the quota was exhausted mid-session. Migrating to `gemini-2.0-flash-lite` resolved both the quota and model availability issues.

**Gunicorn timeout for Gemini calls:** Gemini API calls for image analysis take 10–20 seconds. The default gunicorn timeout of 30 seconds caused worker timeouts under load. Setting `--timeout 120` resolved this.

**Render free tier — no shell access:** Render's free web service tier does not provide a Shell tab. Database seeding and admin account creation, which normally require interactive terminal commands, were automated via `build.sh` and `create_admin_auto.py` using environment variables (`ADMIN_USERNAME`, `ADMIN_PASSWORD`), eliminating the need for shell access entirely.

**PostgreSQL URL format:** Render supplies `DATABASE_URL` as `postgres://...` but SQLAlchemy requires `postgresql://...`. A one-line string replacement in `config.py` handles this automatically without any manual intervention.

---

## Future Scope

- **Real municipal API integration** — direct submission to state government grievance portals (CPGRAMS, state-specific APIs)
- **WhatsApp / SMS notifications** — citizens receive status updates via messaging platforms
- **Autonomous scheduled follow-up** — external scheduler to trigger escalation letters without admin action
- **Community verification** — citizen upvoting to validate reports before escalation
- **Multilingual letters** — Marathi and Hindi complaint letters using Gemini's multilingual capability
- **Predictive issue forecasting** — predict high-risk zones using historical seasonal patterns

---

## Impact

- Bridges the gap between a citizen seeing a problem and having a formally documented, escalatable record
- Recurrence detection exposes chronic infrastructure failures that would otherwise be treated as isolated incidents
- RTI-compatible letters give citizens immediate, usable leverage without requiring legal knowledge or government portal access
- Civic health analytics give administrators and community leaders a structured view of infrastructure health

---

## Learning Outcomes

- Designing multi-role AI agent pipelines with conditional branching (7 distinct Gemini roles)
- Prompt engineering for structured JSON outputs with vision models
- Handling model deprecation and quota limits in production deployments
- Production deployment with Flask + PostgreSQL + Gunicorn on Render
- Automating database setup and admin creation for platforms without shell access
- Database schema design for AI-enriched civic data

---

## Acknowledgements

- [Google AI Studio](https://aistudio.google.com) — Gemini API
- [Leaflet.js](https://leafletjs.com) + [OpenStreetMap](https://openstreetmap.org) — mapping
- [Render](https://render.com) — hosting
- Coding Ninjas × Google for Developers — Vibe2Ship 2026 hackathon
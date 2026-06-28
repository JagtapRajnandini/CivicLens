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
| **Submission Deadline** | 29 June 2026, 2:00 PM |

---

## Elevator Pitch

CivicLens transforms a citizen's photo into a formally documented, tracked, and escalation-ready civic complaint — in under 30 seconds. The AI agent classifies the issue, detects whether it is a recurring problem at the same location, scores its community impact, generates an RTI-compatible grievance letter, and provides a citizen assistant for follow-up guidance. Administrators get an analytics dashboard with AI-generated civic health insights. No government API integration is required — impact is delivered through the document itself.

---

## Problem Overview

Indian citizens face a fragmented, opaque, and unresponsive civic reporting ecosystem:

- Reporting channels (WhatsApp groups, social media) produce no official record.
- Existing portals require manual categorization, department knowledge, and follow-through.
- Chronic problems at the same location are treated as new issues every time.
- Citizens have no usable output from the complaint process — no letter, no tracking, no escalation path.

The result: infrastructure problems go unresolved, accountability is absent, and community frustration compounds.

---

## Solution Overview

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
| **Photo-based reporting** | Upload a photo (JPG, PNG, WEBP, HEIC up to 16MB) — no manual categorization required |
| **Auto GPS coordinates** | Browser geolocation auto-requests coordinates on page load; manual entry available as fallback |
| **AI issue classification** | Gemini Vision identifies issue type from 10 supported categories |
| **Community impact scoring** | AI scores impact 1–10 based on location type, proximity to schools/hospitals, and traffic |
| **Tracking ID** | Each report receives a unique `CL-XXXX` tracking ID |
| **Escalation letter** | Formal RTI-compatible grievance letter generated and downloadable as `.txt` |
| **Citizen AI assistant** | Chat with Gemini to ask questions about the report and next steps |
| **Community feed** | Browse all reports sorted by recurrence, impact, recency, or unresolved status |
| **Issue map** | Leaflet.js map with severity-coded pins for all geotagged reports |
| **Status tracking** | Issues move through: Reported → Under Review → In Progress → Resolved |

### Agentic Behaviors

| Behavior | Trigger | What Happens |
|---|---|---|
| **Recurrence detection** | Every new submission | Agent queries DB for prior reports at the same location + issue type; if found, calls Gemini for pattern analysis and adjusts escalation level |
| **Follow-up escalation** | Admin button | Agent identifies In Progress reports older than 3 days with no follow-up; generates an escalated letter with RTI Act 2005 references |
| **Civic health insights** | `/insights` page | Agent aggregates all report data and generates a civic health score, chronic zone map, and 3 actionable recommendations |

### Administrator Workflow

| Feature | Description |
|---|---|
| **Secure login** | Username/password authentication via Flask-Login |
| **Status management** | Update any report status with one click |
| **Escalation dashboard** | View reports flagged as escalation-due, download follow-up letters |
| **Follow-up generation** | Trigger AI follow-up letter generation for stale In Progress reports |
| **Insights refresh** | Force regeneration of the cached civic health analysis |
| **Summary statistics** | Total reports, pending, in-progress, recurring, escalation-due counts |

---

## AI-Powered Capabilities

CivicLens uses **Google Gemini 2.0 Flash Lite** across 7 distinct roles:

| Role | When Triggered | Purpose |
|---|---|---|
| **1+2 — Vision + Impact** | Every report submission | Analyzes image → classifies issue type (10 categories), severity (1–5), department assignment with reasoning, community impact score (1–10) with reasoning, confidence score |
| **3 — Recurrence Analysis** | When prior reports exist at the same location | Identifies pattern (temporary patching, structural failure, seasonal), sets escalation level (standard / elevated / urgent) |
| **4 — Escalation Letter** | Every report submission | Generates formal RTI-compatible grievance letter in plain text, tailored to the issue type, department, and recurrence history |
| **5 — Follow-Up Letter** | Admin "Generate Follow-Up" action | Generates an escalated follow-up letter for unresolved issues, with RTI Act 2005 references if elapsed > 14 days |
| **6 — Citizen Assistant** | User chat messages on report pages | Answers citizen questions in context of their specific report (department contact, escalation steps, RTI process) |
| **7 — Civic Insights** | `/insights` page (cached 10 min) | Produces civic health score (0–100), top issue breakdown, chronic zone identification, and 3 actionable recommendations |

### Supported Issue Categories

- Pothole
- Broken Streetlight
- Water Leakage
- Garbage / Waste
- Damaged Footpath
- Sewage Overflow
- Fallen Tree
- Road Damage
- Construction Obstruction
- Other

---

## Google AI Studio / Gemini Integration

| Integration Point | Detail |
|---|---|
| **API** | Google Gemini API via `google-genai` Python SDK v2.10.0 |
| **Model** | `gemini-2.0-flash-lite` (all 7 roles) |
| **Multimodal** | Image bytes sent via `types.Part.from_bytes()` with MIME type detection |
| **Structured output** | `response_mime_type='application/json'` enforces JSON-only responses for Roles 1–3 and 7 |
| **Prompt architecture** | Field descriptions only — no JSON templates — to prevent JSON mode conflicts |
| **Error handling** | `json.JSONDecodeError` and API errors handled separately; raw responses logged before parsing |
| **API key** | Obtained from [Google AI Studio](https://aistudio.google.com/app/apikey) |

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
| Database (production) | PostgreSQL (via `psycopg2-binary`) | — |
| Maps | Leaflet.js + OpenStreetMap | 1.9.4 |
| WSGI Server | Gunicorn | 21.2.0 |
| Hosting | Render | — |
| Frontend | Jinja2 templates, plain CSS, minimal JS | — |

---

## High-Level System Architecture

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

## Project Workflow

```
Citizen uploads photo + location
         │
         ▼
Flask saves image → calls Gemini Role 1+2 (Vision + Impact)
         │
         ▼
Query DB: prior reports at same location + same issue type?
         │
    ┌────┴────┐
   Yes        No
    │          │
    ▼          ▼
Gemini Role 3   Skip recurrence
(Recurrence     escalation_level='standard'
 analysis)
    │
    └────┬────┘
         │
         ▼
Gemini Role 4: Generate escalation letter
         │
         ▼
Save complete report to DB → Redirect to confirmation page
         │
         ▼
Citizen sees: AI report, impact score, recurrence flag,
              escalation letter download, AI assistant chat
```

---

## User Roles and Permissions

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

> Citizens do not require registration or login.

---

## Screens and Major Functionality

| Page | Route | Description |
|---|---|---|
| Home | `/` | Live stats (total reports, recurring, resolved), recent 4 report cards |
| Report Issue | `/report` | Photo upload with drag-and-drop, auto GPS, area type — full AI analysis on submit |
| Confirmation | `/confirmation/<id>` | AI report output, severity bar, impact score, recurrence flag, letter download, AI chat |
| Community Feed | `/feed` | All reports sorted by recurring / impact / recent / unresolved |
| Issue Detail | `/issue/<id>` | Full report, status timeline, letters, AI assistant chat |
| Map | `/map` | Leaflet map with severity-coded circle markers, popup details |
| Civic Insights | `/insights` | AI civic health score (0–100), top issues, chronic zones, recommendations |
| Admin | `/admin` | Status update table, escalation due flags, follow-up generation, summary stats |
| Login | `/login` | Admin authentication |

---

## Database Overview

**Three tables:**

**`reports`** — Core entity (25 columns):
- Identity: `id`, `tracking_id` (CL-XXXX)
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
├── create_admin_auto.py      # Automated admin user setup (used in build.sh)
├── build.sh                  # Render build script (install → seed → create admin)
├── Procfile                  # Gunicorn start command
├── runtime.txt               # Python 3.12.10
├── requirements.txt          # Python dependencies
├── .env.example              # Environment variable template
├── services/
│   ├── ai_service.py         # All 7 Gemini roles
│   ├── report_service.py     # Report submission pipeline
│   └── insights_service.py  # DB aggregation for Gemini Role 7
├── templates/
│   ├── base.html             # Base layout (nav, footer)
│   ├── home.html             # Home page
│   ├── report.html           # Issue submission form
│   ├── confirmation.html     # Post-submission results
│   ├── feed.html             # Community feed
│   ├── issue_detail.html     # Full issue view
│   ├── map.html              # Leaflet map
│   ├── insights.html         # Civic health dashboard
│   ├── admin.html            # Admin dashboard
│   └── login.html            # Admin login
├── static/
│   ├── style.css             # Design system — civic color palette, components
│   ├── map.js                # Leaflet map initialization
│   ├── chat.js               # Citizen AI assistant chat
│   └── uploads/              # Uploaded report images (gitignored except placeholder)
```

---

## Installation

### Prerequisites

- Python 3.12+
- Git

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/JagtapRajnandini/CivicLens.git
cd CivicLens

# 2. Create and activate virtual environment
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
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
| `GEMINI_API_KEY` | ✅ | Google AI Studio API key — [Get one here](https://aistudio.google.com/app/apikey) |
| `SECRET_KEY` | ✅ | Flask session secret — generate with `python -c "import secrets; print(secrets.token_hex(32))"` |
| `DATABASE_URL` | ⬜ Production | PostgreSQL connection string (Render sets this automatically for linked databases) |
| `ADMIN_USERNAME` | ⬜ Build | Admin username for automated setup (default: `admin`) |
| `ADMIN_PASSWORD` | ⬜ Build | Admin password for automated setup via `build.sh` |

See `.env.example` for a template.

---

## Deployment on Render

### Initial Setup

1. Push the repository to GitHub.
2. Go to [render.com](https://render.com) → **New → Web Service**.
3. Connect the GitHub repository.
4. Set the following:

| Setting | Value |
|---|---|
| **Environment** | Python |
| **Build Command** | `bash build.sh` |
| **Start Command** | `gunicorn main:app -w 1 --timeout 120` |
| **Python Version** | 3.12.10 (set in `runtime.txt`) |

5. Add environment variables in the Render dashboard:

| Variable | Value |
|---|---|
| `GEMINI_API_KEY` | Your key from Google AI Studio |
| `SECRET_KEY` | A random 32-character string |
| `ADMIN_PASSWORD` | Password for the admin account |

6. (Optional but recommended) Add a **PostgreSQL** database from the Render dashboard and link it to the web service. Render sets `DATABASE_URL` automatically.

7. Deploy. The `build.sh` script installs dependencies, seeds demo data, and creates the admin account automatically.

---

## Demo Credentials

> **Note:** These credentials are for the demo/evaluation environment only.

### Admin Account

| Field | Value |
|---|---|
| **Username** | `admin` |
| **Password** | `CivicLens@2026` |
| **Login URL** | `/login` |

**Admin capabilities:**
- View all submitted reports in a table with sortable columns
- Update issue status (Reported → Under Review → In Progress → Resolved)
- Generate AI follow-up escalation letters for stale In Progress issues
- Download follow-up letters as `.txt` files
- Refresh the civic insights cache
- View escalation-due flags on overdue reports

Citizens do not require login. All report submission and viewing features are publicly accessible.

---

## Future Scope

The following enhancements were identified but not implemented within the hackathon timeline:

- **Real municipal API integration** — direct submission to state government grievance portals (CPGRAMS, state-specific APIs)
- **WhatsApp / SMS notifications** — citizens receive status updates via messaging platforms
- **Scheduled autonomous follow-up** — Render Cron Job to trigger escalation letters without admin action
- **Community verification layer** — citizen upvoting to validate reports before escalation
- **Predictive issue forecasting** — predict high-risk zones using historical seasonal patterns
- **Multilingual support** — Marathi and Hindi complaint letters using Gemini's multilingual capability

---

## Challenges Faced

**Gemini Vision prompt reliability:** The original prompt included a JSON template with angle-bracket placeholders (`"<one of the valid categories>"`). When `response_mime_type='application/json'` is active, this creates a conflict — Gemini sometimes returns the template structure literally. The fix was to remove the JSON template entirely and describe each field in plain English, letting the SDK enforce JSON structure.

**JSON mode and multimodal requests:** Combining `response_mime_type='application/json'` with image input required careful testing to confirm support in the `google-genai` 2.x SDK (which uses a different API surface than the deprecated `google.generativeai` package).

**Gunicorn timeout for Gemini calls:** Gemini API calls for image analysis can take 10–20 seconds. Default gunicorn timeout of 30 seconds caused worker timeouts. Setting `--timeout 120` resolved this.

**PostgreSQL on Render free tier:** Render's free PostgreSQL tier has limited connections. Using `psycopg2-binary` with a single gunicorn worker (`-w 1`) keeps connection count manageable.

---

## Learning Outcomes

- Designing multi-role AI agent pipelines (7 distinct Gemini roles with conditional branching)
- Prompt engineering for structured outputs with vision models
- Distinguishing between agent pipelines (sequential) and agent behavior (conditional, context-aware)
- Production deployment with Flask + PostgreSQL + Gunicorn on Render
- Database schema design for AI-enriched civic data

---

## Impact

- Bridges the gap between a citizen seeing a problem and having a formally documented, escalatable record
- Recurrence detection exposes chronic infrastructure failures that would otherwise be treated as isolated incidents
- RTI-compatible letters give citizens immediate, usable leverage without requiring legal knowledge or government portal access
- Civic health analytics give administrators and community leaders a structured view of infrastructure health

---

## Acknowledgements

- [Google AI Studio](https://aistudio.google.com) — Gemini API
- [Leaflet.js](https://leafletjs.com) + [OpenStreetMap](https://openstreetmap.org) — mapping
- [Render](https://render.com) — hosting
- Coding Ninjas × Google for Developers — Vibe2Ship 2026 hackathon
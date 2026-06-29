# CivicLens — AI-Powered Civic Accountability Platform

<div align="center">

![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0.3-000000?style=flat&logo=flask&logoColor=white)
![Gemini](https://img.shields.io/badge/Gemini_AI-2.0_Flash-4285F4?style=flat&logo=google&logoColor=white)
![Cloud Run](https://img.shields.io/badge/Google_Cloud_Run-4285F4?style=flat&logo=googlecloud&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=flat&logo=sqlite&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=flat)

**Snap a photo. AI analyzes the problem. A formal escalation letter is generated — in under 30 seconds.**

[🌐 Live App](https://civiclens-917815028143.asia-southeast1.run.app) · [📁 Repository](https://github.com/JagtapRajnandini/CivicLens) · [📄 Submission Doc](https://docs.google.com/document/d/1My_zUBl6AuNe4NeJc-VeWB8FaPOk6v-AGC-doZM1n_A/edit?usp=sharing)

</div>

---

## 🏆 Hackathon Information

| | |
|---|---|
| **Hackathon** | Vibe2Ship 2026 — Coding Ninjas × Google for Developers |
| **Problem Statement** | Civic Issue Reporting & Accountability |
| **Track** | AI-Powered Applications using Google Gemini API |
| **Submitted by** | Rajnandini Jagtap |
| **Deployment** | Google Cloud Run (via Google AI Studio) |

---

## 🎯 Elevator Pitch

India loses ₹6,000 crores annually from delayed infrastructure fixes, yet 83% of citizens never report civic issues because they don't know how or who to ask.

CivicLens removes that barrier. A citizen uploads a photo of any infrastructure problem — pothole, broken streetlight, sewage overflow — and Gemini AI takes over: classifying the issue, scoring its severity and community impact, detecting whether it is a recurring problem, routing it to the correct municipal department, and generating a ready-to-submit formal RTI-compatible escalation letter. Everything happens in under 30 seconds, with no civic knowledge required.

---

## 🔍 Problem Overview

Urban India's civic accountability gap has three structural causes:

**Citizens don't know how to report.** Filing a civic complaint requires knowing the correct municipal department, the right form, and the right language — knowledge most people don't have.

**Problems repeat without consequence.** The same pothole gets reported 15 times over 6 months. Without pattern detection, each report is treated as new, and systemic problems are never escalated.

**Formal escalation is inaccessible.** RTI (Right to Information) letters and formal complaints require precise legal language. Most citizens can't write them and can't afford to pay someone who can.

---

## ✅ Solution Overview

CivicLens is a full-stack web application that uses a **multi-role Gemini AI pipeline** to transform a photo and a location into a complete, actionable civic complaint with a formal escalation letter — automatically.

The workflow is:
1. Citizen uploads a photo and enters the location
2. Gemini Vision classifies the issue and scores severity
3. The system checks whether this location has prior reports (recurrence detection)
4. Gemini generates a formal escalation letter addressed to the correct department
5. The report is visible on a community feed and interactive map
6. If the issue is not resolved within 3 days, an autonomous follow-up letter is generated
7. Aggregated AI analysis generates a Civic Health Report across all reports

---

## ⭐ Key Features

| Feature | Description |
|---|---|
| **Photo-Based Reporting** | Upload JPG, PNG, WEBP, or HEIC images up to 16 MB |
| **GPS Auto-Detection** | Browser geolocation with fallback to manual coordinate entry |
| **AI Image Analysis** | Gemini Vision classifies issue type, severity, affected department |
| **Recurrence Detection** | Detects whether the same location has been reported before |
| **Escalation Letter Generation** | Formal RTI-ready letter, downloadable as `.txt` |
| **Community Feed** | Public feed sortable by impact, recurrence, recency, or status |
| **Interactive Map** | Leaflet.js map with colour-coded severity pins for all geotagged reports |
| **Issue Tracking** | Unique tracking ID (`CL-XXXX`) for every report |
| **AI Assistant Chat** | Per-report conversational assistant for citizen guidance |
| **Admin Dashboard** | Status management with per-row status updates |
| **Autonomous Follow-Up** | Auto-generates follow-up letters for stale `in_progress` reports (3+ days) |
| **Civic Health Report** | AI-generated insights: health score, top issues, chronic zones, recommendations |

---

## 🤖 AI-Powered Features

CivicLens uses **6 distinct Gemini AI roles**, each with a focused prompt:

### Role 1 — Vision Analysis (`gemini-2.0-flash` with `gemini-1.5-flash` fallback)
Receives the photo, location, and area type. Returns a structured JSON response containing:
- Issue type (from 11 categories: Pothole, Broken Streetlight, Water Leakage, Sewage Overflow, Road Damage, Garbage and Waste, Damaged Footpath, Fallen Tree, Construction Obstruction, Open Manhole, Other)
- Severity score (1–5)
- Natural-language description
- Responsible department and routing reasoning
- Confidence score

### Role 2 — Impact Scoring (`gemini-1.5-flash`)
Evaluates the community impact of the specific issue and location context. Returns a 1–10 impact score with written justification used in the escalation letter.

### Role 3 — Recurrence Analysis (`gemini-1.5-flash`)
Compares the new report against all prior reports at the same location. Determines whether the problem is recurring, how many times it has occurred, and what the pattern suggests about departmental responsiveness.

### Role 4 — Escalation Letter Generation (`gemini-1.5-flash`)
Generates a formal RTI-compatible letter addressed to the correct department. Includes the issue description, location, severity, recurrence data, and a formal demand for action. Downloadable as a `.txt` file.

### Role 5 — Autonomous Follow-Up Letter (`gemini-1.5-flash`)
Triggered automatically when a report has been `in_progress` for more than 3 days without resolution. Generates a stronger follow-up letter referencing the original complaint, elapsed time, and regulatory obligations.

### Role 6 — Citizen AI Assistant (`gemini-1.5-flash`)
A conversational assistant anchored to the specific report. Answers citizen questions about escalation steps, department contacts, RTI procedures, and expected timelines. Conversation history is persisted in the database.

### Role 7 — Civic Health Insights (`gemini-1.5-flash`)
Analyses aggregated statistics across all reports (issue type distribution, severity patterns, chronic zones, resolution rates) and generates a structured Civic Health Report with a 0–100 health score, top issue analysis, chronic zone identification, and actionable recommendations for city administrators.

---

## 🔧 Google AI Studio & Gemini Integration

### How Gemini is Used

CivicLens calls the Gemini API directly from the Flask backend using the official `google-genai` Python SDK (`google-genai==2.10.0`). All API calls are server-side — the API key is never exposed to the browser.

**Models used:**
- `gemini-2.0-flash` — Primary vision model for image analysis (Role 1). Automatically falls back to `gemini-1.5-flash` if the primary model is unavailable.
- `gemini-1.5-flash` — All text-generation roles (Roles 2–7)

### How Google AI Studio is Used

The live deployment at `civiclens-917815028143.asia-southeast1.run.app` was deployed directly from **Google AI Studio** using its **Deploy to Cloud Run** feature. This process:
- Containerises the Flask application automatically
- Deploys it to **Google Cloud Run** in the `asia-southeast1` region
- Injects the `GEMINI_API_KEY` securely as a server-side environment variable
- Provides a public HTTPS URL with auto-scaling

> **Important:** The Flask backend is **not** hosted inside Google AI Studio itself. Google AI Studio is the deployment pipeline. The runtime is **Google Cloud Run**. This is the standard deployment path for apps built in or submitted through AI Studio.

### API Key Management

| Environment | Key Location |
|---|---|
| Local development | `.env` file (never committed) |
| Google Cloud Run | Injected by AI Studio deploy pipeline |

---

## 🛠️ Technology Stack

| Layer | Technology |
|---|---|
| **Backend** | Python 3.12, Flask 3.0.3 |
| **AI** | Google Gemini API (`gemini-2.0-flash`, `gemini-1.5-flash`) via `google-genai 2.10.0` |
| **Database** | SQLite (via Flask-SQLAlchemy 3.1.1) |
| **ORM** | SQLAlchemy 2.x |
| **Frontend** | Jinja2 templates, vanilla JavaScript, custom CSS |
| **Maps** | Leaflet.js (CDN) with OpenStreetMap tiles |
| **Image Processing** | Pillow 12.2.0 (resize before Gemini Vision) |
| **WSGI Server** | Gunicorn 21.2.0 |
| **Deployment** | Google Cloud Run (via Google AI Studio) |
| **Environment** | python-dotenv 1.0.1 |

---

## 🏗️ High-Level Architecture

```
Browser
  │
  ├── GET /report          → report.html (GPS + image upload form)
  ├── POST /report         → report_service.py
  │                              ├── saves image to static/uploads/
  │                              ├── ai_service.analyze_image()      → Gemini Vision
  │                              ├── ai_service.score_impact()       → Gemini Text
  │                              ├── ai_service.analyze_recurrence() → Gemini Text
  │                              └── ai_service.generate_escalation_letter() → Gemini Text
  │
  ├── GET /feed            → feed.html    (sortable community feed)
  ├── GET /issue/<id>      → issue_detail.html (full analysis + AI chat)
  ├── POST /chat/<id>      → ai_service.chat_with_assistant() → Gemini Text
  ├── GET /map             → map.html     (Leaflet.js)
  ├── GET /map/data        → JSON of all geotagged reports
  ├── GET /admin           → admin.html   (status management + auto follow-up trigger)
  ├── POST /admin/update   → status update per report
  └── GET /insights        → ai_service.generate_civic_insights() → Gemini Text

services/
  ├── ai_service.py        (all 7 Gemini roles)
  ├── report_service.py    (submission pipeline orchestration)
  └── insights_service.py  (SQL aggregation for insights payload)
```

---

## 📋 Project Workflow

```
Citizen                          CivicLens                        Gemini API
   │                                 │                                 │
   │── Upload photo + location ──►   │                                 │
   │                                 │── analyze_image() ─────────────►│
   │                                 │◄── issue_type, severity, dept ──│
   │                                 │── score_impact() ──────────────►│
   │                                 │◄── impact_score, reasoning ─────│
   │                                 │── analyze_recurrence() ────────►│
   │                                 │◄── is_recurring, pattern ───────│
   │                                 │── generate_escalation_letter() ►│
   │                                 │◄── formal letter text ──────────│
   │◄── Confirmation + letter ───    │                                 │
   │                                 │                                 │
   │── Ask AI assistant ──────────►  │── chat_with_assistant() ───────►│
   │◄── Contextual guidance ──────   │◄── response ────────────────────│
   │                                 │                                 │
Admin                                │                                 │
   │── Visit /admin ─────────────►   │                                 │
   │                                 │ [if in_progress > 3 days]       │
   │                                 │── generate_followup_letter() ──►│
   │                                 │◄── follow-up letter ────────────│
   │◄── Dashboard + auto letters ─   │                                 │
```

---

## 👥 User Roles & Permissions

| Role | Access | Notes |
|---|---|---|
| **Citizen** | `/`, `/report`, `/feed`, `/issue/<id>`, `/map`, `/insights`, AI chat | No login required |
| **Administrator** | All citizen pages + `/admin`, `/admin/update`, letter downloads | Login required (see Demo Credentials below) |

---

## 📱 Major Screens & Functionalities

### Home (`/`)
Live stats (total reports, recurring issues, resolved count) and a grid of the 4 most recent reports. Entry point for new citizens.

### Report Form (`/report`)
- GPS auto-detection with state feedback (detecting / success / denied / error / unsupported)
- Retry button for denied or failed GPS requests
- Drag-and-drop or click-to-upload image with live preview
- Manual coordinate entry as fallback (with link to Google Maps)
- Form submission guard validates coordinates before sending
- AI analysis takes 10–20 seconds after submission

### Confirmation (`/confirmation/<tracking_id>`)
Displays the full AI analysis result: issue type, severity bar, impact score, department routing, recurrence data, and a download link for the escalation letter.

### Community Feed (`/feed`)
All reports, sortable by: Recurring First (default), Highest Impact, Most Recent, Unresolved Only. Each card shows image, type, severity, impact, recurring badge, and status.

### Issue Detail (`/issue/<id>`)
Full report detail: AI analysis panel, recurrence block, escalation letter preview + download, follow-up letter preview + download (if generated), embedded AI assistant chat.

### Issue Map (`/map`)
Leaflet.js interactive map. All geotagged reports appear as colour-coded circle markers (green = resolved, orange = in progress, red = urgent/recurring). Clicking a marker shows a popup with tracking ID, type, and a link to the detail page.

### Admin Dashboard (`/admin`)
Table of all reports with inline status dropdown and per-row update form. Summary stats row (total / pending / escalation due). Automatically generates follow-up letters for `in_progress` reports older than 3 days on page load. Escalation due badge triggers letter download link.

### Civic Health Report (`/insights`)
Requires 5+ reports. Shows: Civic Health Score (0–100, colour-coded), Resolution Analysis paragraph, Top Issue Types with average severity, Chronic Zones (locations with 3+ reports), AI Recommendations list.

---

## 🗃️ Database Overview

**Table: `reports`**

| Column | Type | Description |
|---|---|---|
| `id` | Integer PK | Auto-increment |
| `tracking_id` | String(20) | Unique `CL-XXXX` identifier |
| `image_path` | String(255) | Relative path under `static/uploads/` |
| `location_text` | String(500) | Human-readable location description |
| `area_type` | String(50) | `residential`, `commercial`, `school_zone`, `main_road`, `industrial` |
| `issue_type` | String(100) | Gemini-classified category |
| `severity` | Integer | 1–5 (Gemini Role 1) |
| `description` | Text | AI-generated description |
| `department` | String(100) | Responsible department |
| `department_reasoning` | Text | Why this department was selected |
| `impact_score` | Integer | 1–10 (Gemini Role 2) |
| `impact_reasoning` | Text | Community impact justification |
| `confidence_score` | Float | AI classification confidence (0–1) |
| `is_recurring` | Boolean | Recurrence flag (Gemini Role 3) |
| `recurrence_count` | Integer | Number of prior reports at this location |
| `recurrence_pattern` | Text | Pattern description |
| `escalation_level` | String(20) | `standard`, `urgent`, `critical` |
| `escalation_letter` | Text | Full letter text (Gemini Role 4) |
| `followup_letter` | Text | Follow-up letter text (Gemini Role 5) |
| `followup_generated_at` | DateTime | When follow-up was auto-generated |
| `escalation_due` | Boolean | Whether escalation is due |
| `latitude` | Float | GPS latitude (nullable) |
| `longitude` | Float | GPS longitude (nullable) |
| `status` | String(30) | `reported`, `under_review`, `in_progress`, `resolved` |
| `created_at` | DateTime | UTC timestamp |

**Table: `chat_messages`**

| Column | Type | Description |
|---|---|---|
| `id` | Integer PK | Auto-increment |
| `report_id` | Integer FK | References `reports.id` |
| `role` | String(10) | `user` or `assistant` |
| `content` | Text | Message text |
| `created_at` | DateTime | UTC timestamp |

---

## 📁 Folder Structure

```
CivicLens/
├── main.py                    # Flask app + all route handlers
├── config.py                  # Configuration class with env var validation
├── models.py                  # SQLAlchemy models: Report, ChatMessage
├── seed.py                    # Demo data seeder (8 pre-analysed reports)
│
├── services/
│   ├── __init__.py
│   ├── ai_service.py          # All 7 Gemini roles
│   ├── report_service.py      # Report submission pipeline orchestration
│   └── insights_service.py    # SQL aggregation queries for Civic Health
│
├── templates/
│   ├── base.html              # Navigation, flash messages, footer
│   ├── home.html              # Landing page with live stats
│   ├── report.html            # Report form (GPS + image upload)
│   ├── confirmation.html      # Post-submission result page
│   ├── feed.html              # Community feed with sort controls
│   ├── issue_detail.html      # Full report detail + AI chat
│   ├── map.html               # Leaflet.js interactive map
│   ├── admin.html             # Admin status management dashboard
│   └── insights.html          # Civic Health Report
│
├── static/
│   ├── style.css              # Full custom CSS design system
│   ├── chat.js                # AI assistant chat WebSocket-free handler
│   ├── map.js                 # Leaflet map initialisation
│   └── uploads/               # User-uploaded images (gitignored)
│
├── requirements.txt
├── Procfile                   # gunicorn main:app --workers 1 --timeout 120
├── runtime.txt                # python-3.12.3
├── .env.example               # Environment variable reference
└── .gitignore
```

---

## ⚙️ Installation Guide

### Prerequisites

- Python 3.12+
- A Google Gemini API key (free tier available at [Google AI Studio](https://aistudio.google.com/app/apikey))
- Git

### Clone the Repository

```bash
git clone https://github.com/JagtapRajnandini/CivicLens.git
cd CivicLens
```

### Create and Activate a Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🔑 Environment Variables

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

```env
# Required: Google Gemini API key
# Get yours free at: https://aistudio.google.com/app/apikey
GEMINI_API_KEY=your_gemini_api_key_here

# Required: Flask session secret key
# Generate: python -c "import secrets; print(secrets.token_hex(32))"
SECRET_KEY=your_secret_key_here

# Optional: Enable debug mode — NEVER set true in production
FLASK_DEBUG=false
```

---

## 🚀 Local Setup

```bash
# 1. Run the app
python main.py
# or
python -m flask --app main run

# 2. Open in browser
# http://127.0.0.1:5000

# 3. (Optional) Load demo data
python seed.py
```

The database (`instance/civiclens.db`) is created automatically on first run. The `static/uploads/` directory is created automatically.

---

## ☁️ Deployment

### Google Cloud Run (via Google AI Studio) — Live Deployment

The live application is deployed on **Google Cloud Run** in the `asia-southeast1` region. Deployment was done using Google AI Studio's **Deploy to Cloud Run** feature, which containerises the Flask app and injects the `GEMINI_API_KEY` securely into the server environment.

**Live URL:** `https://civiclens-917815028143.asia-southeast1.run.app`

### Manual Deployment (Alternative)

CivicLens can also be deployed to any platform that supports Python/Gunicorn, such as Render.com:

**Build command:**
```
pip install -r requirements.txt
```

**Start command:**
```
gunicorn main:app --workers 1 --timeout 120
```

Required environment variables: `GEMINI_API_KEY`, `SECRET_KEY`

> **SQLite note:** SQLite is used as the database. On ephemeral hosting platforms (Cloud Run, Render), the database resets on each redeploy. For production use, replace with PostgreSQL.

---

## 🔗 Live Links

| Resource | URL |
|---|---|
| **Live Application** | https://civiclens-917815028143.asia-southeast1.run.app |
| **GitHub Repository** | https://github.com/JagtapRajnandini/CivicLens |
| **Submission Document** | https://docs.google.com/document/d/1My_zUBl6AuNe4NeJc-VeWB8FaPOk6v-AGC-doZM1n_A/edit?usp=sharing |

---

## 🔐 Demo Credentials

| Role | Access | Credentials |
|---|---|---|
| **Citizen** | No login required — visit [/report](https://civiclens-917815028143.asia-southeast1.run.app/report) to file a report | — |
| **Admin** | Login required to access `/admin` dashboard | **Username:** `admin` · **Password:** `CivicLens@2026` |

---

## 🔭 Future Scope

- **Role-based access** — Separate portals for citizen, department officer, and super-admin roles
- **PostgreSQL** — Persistent database for production deployments
- **Push Notifications** — Status change alerts for citizens via email or SMS
- **Multilingual Support** — Report submission and letters in regional Indian languages
- **Department Portal** — Dedicated view for municipal department officers
- **Mobile PWA** — Progressive Web App with offline photo capture
- **Analytics Dashboard** — Ward-level heatmaps and trend charts for city planners
- **Bulk Escalation** — Auto-bundle recurring issues at the same location into a single escalation batch
- **Resolved Verification** — Require photo evidence from authorities to close reports

---

## 🧗 Challenges Faced

**Structured JSON from Gemini Vision** — Getting Gemini to reliably return parseable JSON with correct field types required multi-stage prompt engineering with explicit schema definitions, response MIME type enforcement, and graceful fallback to safe defaults on every parse failure.

**Gemini model selection** — `gemini-2.0-flash` offers superior vision capability but has different availability characteristics than `gemini-1.5-flash`. Implementing a primary/fallback chain with per-exception logging required careful error handling.

**Gunicorn timeout with AI calls** — Gemini API calls for complex analysis take 10–20 seconds. Gunicorn's default 30-second worker timeout killed requests mid-analysis. The fix was `--timeout 120`.

**SQLite concurrency** — Multiple Gunicorn workers cause SQLite write-lock errors. The fix was `--workers 1`, which is safe for a hackathon workload but limits throughput.

**GPS accuracy on mobile** — `enableHighAccuracy: true` triggers a 12-second GPS acquisition on first use. The location state machine handles detecting / success / denied / error / unsupported states without blocking the user from entering coordinates manually.

**Recurrence detection without embeddings** — Without a vector database, recurrence is detected by SQL query on `location_text` and `issue_type`. This works well for exact and near-exact location strings but would miss paraphrase variants in production.

---

## 📚 Learning Outcomes

- Designing multi-role Gemini prompt pipelines with per-role structured output schemas
- Primary/fallback model chains using the `google-genai` 2.x SDK
- Autonomous background actions triggered by page load (follow-up letter generation)
- Building civic-domain AI applications with RTI-compatible formal language generation
- Deploying Flask applications to Google Cloud Run via Google AI Studio
- GPS browser API state machine design for graceful degradation
- Integrating Leaflet.js with a dynamic Flask JSON endpoint

---

## 💡 Impact

- **Citizens** gain a voice without needing legal knowledge, civic expertise, or knowing which department to contact.
- **Recurring issues** are surfaced automatically, creating accountability pressure on departments.
- **Formal letters** are accessible to everyone — not just those who can afford legal help.
- **City administrators** get an AI-generated Civic Health Report showing the worst-affected areas and actionable recommendations.

India loses ₹6,000 crores annually from delayed infrastructure fixes (NITI Aayog, 2023). CivicLens makes the first step — reporting and escalating — frictionless for every citizen.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

## 🙏 Acknowledgements

- [Google Gemini API](https://ai.google.dev/) — Multimodal AI powering all 7 roles
- [Google AI Studio](https://aistudio.google.com/) — Development environment and Cloud Run deployment
- [Leaflet.js](https://leafletjs.com/) — Open-source interactive maps
- [OpenStreetMap](https://www.openstreetmap.org/) — Map tiles
- [Flask](https://flask.palletsprojects.com/) — Python web framework
- [Vibe2Ship 2026](https://codingninjas.com) — Coding Ninjas × Google for Developers hackathon
- NITI Aayog 2023 infrastructure loss statistics and Urban Governance Survey 2024 cited for problem framing
# CareBridge AI — Post-Discharge Healthcare Coordination Platform

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg?style=flat&logo=FastAPI&logoColor=white)](https://fastapi.tiangolo.com)
[![Flutter](https://img.shields.io/badge/Flutter-3.x-02569B.svg?style=flat&logo=Flutter&logoColor=white)](https://flutter.dev)
[![React](https://img.shields.io/badge/React-18.x-61DAFB.svg?style=flat&logo=React&logoColor=black)](https://react.dev)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-D71F00.svg?style=flat&logo=SQLAlchemy&logoColor=white)](https://www.sqlalchemy.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16+-336791.svg?style=flat&logo=PostgreSQL&logoColor=white)](https://www.postgresql.org)
[![SQLite](https://img.shields.io/badge/SQLite-3-003B57.svg?style=flat&logo=SQLite&logoColor=white)](https://www.sqlite.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**CareBridge AI** is an intelligent, patient-centric healthcare journey coordination platform designed to bridge the post-discharge care gap. It organizes hospital discharge summaries and clinical instructions into reviewable, actionable journey milestones, tracks diagnostic reports, coordinates shared caregiving responsibilities, and monitors daily medication adherence.

> [!NOTE]
> **Clinical Safety Disclaimer**: CareBridge AI assists with administrative coordination and task organization. It does **not** diagnose, prescribe, modify clinical treatments, or replace qualified medical professionals. All AI-extracted tasks are presented in **draft review mode** requiring patient/clinician verification.

---

## 🌟 Key Features

- **Personalized Healthcare Journeys**: Converts complex post-op or chronic care regimens into step-by-step daily timelines with priority flags (`High`, `Medium`, `Routine`).
- **Caregiver Collaboration**: Secure role-based delegation allowing family caregivers to monitor tasks, mark completed duties, and log observations without altering clinical orders.
- **Medication Adherence Tracker**: Daily dose logging, time-slotted tracking, and adherence streak monitoring to prevent missed medications.
- **Diagnostic & Report Checklist**: Tracks pending laboratory tests, radiology scans, and post-discharge consultations with real-time availability statuses.
- **Dual Client Ecosystem**:
  - **Web Dashboard (React 18 + Tailwind CSS)**: Comprehensive care management portal for patients and clinical coordinators.
  - **Mobile Application (Flutter 3 + Material 3)**: Cross-platform mobile app for iOS, Android, and Web with offline token persistence and quick server switching.
- **AI-Assisted Document Processing**:
  - Scoped document uploads (PDF, JPG, PNG up to 10 MB).
  - Text extraction with **PyMuPDF** and OCR adapter with **Tesseract**.
  - Structured data extraction using OpenAI/Gemini-compatible LLM endpoints with safe, zero-cost simulated fallback mode.
- **Presentation Decks for Pitching**: Includes pre-built 8-slide judge pitch decks (`CareBridge_Pitch_Deck_8_Slides.pptx`) with generated infographics and market analysis charts.

---

## 🌐 Live Deployments & Endpoints

| Service | Target URL | Description |
| :--- | :--- | :--- |
| **Backend REST API** | [https://carebridge-1-9b9i.onrender.com/api](https://carebridge-1-9b9i.onrender.com/api) | Production cloud API on Render |
| **Swagger Interactive Docs** | [https://carebridge-1-9b9i.onrender.com/docs](https://carebridge-1-9b9i.onrender.com/docs) | OpenAPI interactive documentation |
| **API Health Check** | [https://carebridge-1-9b9i.onrender.com/api/health](https://carebridge-1-9b9i.onrender.com/api/health) | Health & operational status check |

---

## 🏗️ Architecture & Technology Stack

```
                              ┌──────────────────────────────────────────────┐
                              │            Clients & Presentation            │
                              ├──────────────────────┬───────────────────────┤
                              │ React Web Dashboard  │  Flutter Mobile App   │
                              │ (Vite + TailwindCSS) │ (Android/iOS/Web/Win) │
                              └──────────┬───────────┴───────────┬───────────┘
                                         │                       │
                                         ▼                       ▼
                              ┌──────────────────────────────────────────────┐
                              │           FastAPI REST API Gateway           │
                              │  • JWT Auth & Scoped Role Access Control     │
                              │  • Journey & Adherence Engine                │
                              │  • PyMuPDF / Tesseract Document Ingestion    │
                              │  • OpenAI / Gemini Structured Extraction     │
                              └──────────────────────┬───────────────────────┘
                                                     │
                                                     ▼
                              ┌──────────────────────────────────────────────┐
                              │         SQLAlchemy 2.0 ORM Engine            │
                              ├──────────────────────┬───────────────────────┤
                              │ Local: SQLite File   │ Cloud: PostgreSQL     │
                              │ (`carebridge.db`)    │ (Render / Supabase)   │
                              └──────────────────────┴───────────────────────┘
```

### Stack Breakdown

- **Backend**: Python 3.11+, [FastAPI](https://fastapi.tiangolo.com/), [SQLAlchemy 2.0](https://www.sqlalchemy.org/), [Pydantic v2](https://docs.pydantic.dev/), [PyJWT](https://pyjwt.readthedocs.io/), [Uvicorn](https://www.uvicorn.org/).
- **Database**: **SQLite** (default zero-configuration local DB) and **PostgreSQL** with modern `psycopg` v3 driver.
- **Web Frontend**: [React 18](https://react.dev/), [Vite](https://vitejs.dev/), [Tailwind CSS](https://tailwindcss.com/), [Lucide React](https://lucide.dev/), [Recharts](https://recharts.org/), [Axios](https://axios-http.com/).
- **Mobile Frontend**: [Flutter 3.x](https://flutter.dev/) (Dart 3), Material 3 Design, `http`, `intl`, `shared_preferences`.
- **Document Processing**: `pymupdf` (PDF text extraction), `pillow` & `pytesseract` (Image OCR).

---

## 👥 Demo Accounts (Pre-Seeded)

When running with `DEMO_MODE=true` (default), the database automatically seeds pre-configured demo users:

| Role | Username / Email | Password | Primary Functions |
| :--- | :--- | :--- | :--- |
| **Patient** | `demo@carebridge.ai` | `carebridge123` | View full journey, log medications, view reports, invite caregivers |
| **Primary Caregiver** | `priya.demo@carebridge.ai` | `carebridge123` | Track assigned tasks, log care observations, assist patient |
| **Secondary Caregiver** | `rohan.demo@carebridge.ai` | `carebridge123` | View emergency contacts, medication schedule, report statuses |

> *Note: All patient and clinical records in demo mode are synthetic and fictional.*

---

## 🚀 Quick Start Guide

### Prerequisites
- **Python**: 3.11 or 3.12 installed ([python.org](https://www.python.org/))
- **Node.js**: 18+ and npm installed ([nodejs.org](https://nodejs.org/))
- **Flutter SDK**: 3.13+ installed ([flutter.dev](https://flutter.dev/)) *(only needed for mobile development)*

---

### 1. Backend Setup

```powershell
# Navigate to backend directory
cd backend

# Create and activate virtual environment (optional)
python -m venv .venv
.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Configure environment
Copy-Item .env.example .env

# Launch API server
```

- API Server: `http://127.0.0.1:8000`
- Swagger Docs: `http://127.0.0.1:8000/docs`
- Health Check: `http://127.0.0.1:8000/api/health`

---

### 2. Web Frontend Setup

In a new terminal:

```powershell
# Navigate to frontend directory
cd frontend

# Install npm dependencies
npm install

# Start Vite development server
npm run dev
```

- Web Dashboard opens at: `http://localhost:5173`
- Default API target: `http://localhost:8000/api` (configurable via `VITE_API_URL` in `.env`).

---

### 3. Flutter Mobile App Setup

In a new terminal:

```powershell
# Navigate to mobile directory
cd mobile

# Fetch Flutter dependencies
flutter pub get

# Check connected devices
flutter devices
```

#### Run on Chrome / Web:
```powershell
flutter run -d chrome
```

#### Run on Windows Desktop:
```powershell
flutter run -d windows
```

#### Run on Android Device / Emulator:
```powershell
flutter run -d <device_id>
```

#### Build Android APK:
```powershell
# Debug APK (Fastest build for testing on physical devices)
flutter build apk --debug

# Release APK
flutter build apk --release
```
*Generated APK will be located at: `mobile/build/app/outputs/flutter-apk/app-debug.apk`.*

---

## 📱 Mobile App: Multi-Server Environment Selector

The Flutter mobile app includes a built-in server switcher directly on the Login screen:
1. **Render Cloud**: Connects to the live cloud backend (`https://carebridge-1-9b9i.onrender.com/api`).
2. **Localhost (8000)**: Connects to local PC backend (`http://127.0.0.1:8000/api`) when running on Desktop or Web.
3. **Android Emulator**: Automatically routes through the Android loopback bridge (`http://10.0.2.2:8000/api`).

---

## 🗄️ Database Architecture & Models

CareBridge dynamically toggles between **SQLite** and **PostgreSQL** using [`backend/app/database/connection.py`](backend/app/database/connection.py).

### Core Database Entities

| Table | Model Class | Description |
| :--- | :--- | :--- |
| `users` | `User` | User accounts, secure hashed credentials, and system roles (`patient`, `caregiver`, `clinician`, `admin`). |
| `patient_profiles` | `PatientProfile` | Patient demographics, preferred language, emergency contact info. |
| `caregiver_relationships` | `CaregiverRelationship` | Links between patients and designated caregivers with fine-grained access control. |
| `healthcare_journeys` | `HealthcareJourney` | The patient's overarching care track (e.g., *Post-Cardiac Surgery Recovery*). |
| `journey_tasks` | `JourneyTask` | Individual actionable tasks, medication times, follow-up appointments, and reminders. |
| `patient_medications` | `PatientMedication` | Prescribed medications, dosage instructions, frequencies, and adherence logs. |
| `required_reports` | `RequiredReport` | Required post-discharge diagnostics (e.g. CBC, Lipid Profile, Echocardiogram). |
| `documents` | `Document` | Uploaded discharge summaries, lab reports, and imaging documents. |
| `notifications` | `Notification` | System notifications, alerts, and care reminders. |
| `barriers` | `Barrier` | Social determinants and care obstacles (transportation, financial, language). |
| `audit_logs` | `AuditLog` | Comprehensive security and access logs for healthcare audit compliance. |

---

## 🤖 AI & OCR Configuration

CareBridge AI operates seamlessly **without any paid API keys**:
- **Simulated Mode (Default)**: When `AI_API_KEY` is not present, the system operates in a deterministic simulated review mode. It extracts raw text using PyMuPDF and produces structured drafts without generating hallucinations.
- **LLM-Powered Mode**: To enable live structured extraction:
  ```env
  AI_API_KEY=your_gemini_or_openai_api_key
  AI_MODEL=gemini-1.5-flash  # or gpt-4o-mini
  AI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/ # for Gemini
  ```
- **Tesseract OCR (Optional)**: For scanned image PDFs or photos, install the [Tesseract-OCR](https://github.com/tesseract-ocr/tesseract) binary and ensure it is on your system PATH.

---

## 📂 Repository Layout

```text
MediCare/
├── backend/                       # FastAPI Python Backend
│   ├── app/
│   │   ├── core/                  # Security, JWT, configuration
│   │   ├── database/              # SQLAlchemy models, connection, migrations
│   │   ├── routers/               # API endpoints (auth, journeys, tasks, reports, etc.)
│   │   ├── schemas/               # Pydantic v2 validation models
│   │   └── services/              # AI service, OCR adapters, demo seeding
│   ├── migrations/                # Alembic migration scripts
│   ├── tests/                     # Automated API test suite
│   ├── requirements.txt           # Python dependencies
│   └── carebridge.db              # SQLite development database
│
├── frontend/                      # React 18 Web Dashboard
│   ├── src/                       # Components, pages, hooks, services
│   ├── package.json               # Node.js dependencies
│   └── vite.config.js             # Vite configuration
│
├── mobile/                        # Flutter Cross-Platform Mobile App
│   ├── lib/
│   │   ├── core/                  # API client, app theme, constants
│   │   ├── models/                # Dart data models
│   │   ├── screens/               # Login, Journey, Medications, Reports, Profile
│   │   ├── services/              # AuthService, JourneyService, etc.
│   │   └── main.dart              # App entrypoint
│   ├── android/                   # Android native configuration
│   └── pubspec.yaml               # Flutter dependencies
│
├── ppt_assets/                    # Generated charts & visuals for presentations
├── CareBridge_Pitch_Deck_8_Slides.pptx  # 8-slide judge pitch presentation
├── render.yaml                    # Render Cloud deployment blueprint
└── README.md                      # Project documentation
```

---

## 🛠️ Testing & Quality Assurance

### Backend API Tests
```powershell
cd backend
python -m unittest discover -s tests -p "test_*.py" -v
```

### Frontend Build Verification
```powershell
cd frontend
npm run build
```

### Flutter Mobile Tests
```powershell
cd mobile
flutter test
```

---

## 🔒 Security & Privacy

- **Cryptographic Security**: Passwords hashed using `scrypt` via Passlib; API access controlled via expiring signed HMAC-SHA256 JWT tokens.
- **Strict Role Boundaries**: Caregivers can only access records specifically delegated to them; clinical wording cannot be modified by caregivers.
- **Upload Integrity**: Strict file type signature inspection and max size limits (10 MB).
- **Human-in-the-Loop Review**: All AI-extracted tasks require explicit patient or clinician review before becoming active tasks.

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

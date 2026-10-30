# CareBridge AI

CareBridge AI is a healthcare journey coordination MVP for patients and caregivers after a hospital visit. It organizes clinician-provided instructions into reviewable journey tasks, tracks administrative report availability, shares selected work with caregivers, and records access barriers.

It does not diagnose, prescribe, change treatment instructions, or replace a healthcare professional. AI extraction is a draft and requires patient review. When no AI key is configured, uploaded documents are handled in clearly labeled simulated mode; the app does not invent tasks from arbitrary text.

## What's included

- React, Vite, Tailwind CSS, React Router, Axios, Recharts, and Lucide icons.
- FastAPI REST API with JWT authentication and patient/caregiver roles.
- SQLAlchemy models for users, patient profiles, caregiver relationships, documents, journeys, tasks, required reports, notifications, barriers, and audit logs.
- PostgreSQL support through `DATABASE_URL`; SQLite is the local default.
- Alembic initial migration.
- Securely scoped document upload and preview for PDF/JPG/PNG, max 10 MB by default; selectable text extraction for PDFs and an optional Tesseract adapter for images.
- OpenAI-compatible structured extraction integration, configured only on the backend through environment variables.
- Fictional demo data and a demo account.

## Demo account

Start the API with `DEMO_MODE=true` (the default in local settings), then sign in:

- Patient: `demo@carebridge.ai` / `carebridge123`
- Caregiver: `priya.demo@carebridge.ai` / `carebridge123`
- Caregiver: `rohan.demo@carebridge.ai` / `carebridge123`

These accounts and all associated clinical-looking details are fictional sample data. Do not add real patient information to the demo workspace.

## Local development

Requirements: Python 3.11+ and Node.js 18+.

### Backend

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload --port 8000
```

The default `DATABASE_URL` is a local SQLite file at `backend/carebridge.db`. Startup creates the schema and seeds fictional data if the demo patient does not exist. The API root at `http://localhost:8000/` returns service links; API docs are at `http://localhost:8000/docs` and the health check is at `http://localhost:8000/api/health`.

To reset fictional demo data, stop the API, delete `backend/carebridge.db`, and restart with `DEMO_MODE=true`.

Set `DATABASE_URL` to a PostgreSQL connection string to use PostgreSQL. For an explicit migration, run `alembic upgrade head` from `backend/`. The development server's metadata initialization is convenient for local first run; use migrations as the controlled schema change mechanism for deployed environments.

### Frontend

In another terminal:

```powershell
cd frontend
npm install
Copy-Item .env.example .env
npm run dev
```

The frontend defaults to `http://localhost:8000/api`. Set `VITE_API_URL` to the deployed API URL plus `/api` when needed. Vite prints the local URL, normally `http://localhost:5173`.

### AI and OCR configuration

The API runs without a paid AI provider. With no `AI_API_KEY`, upload analysis returns a simulated review and does not create generated medical instructions. To enable actual structured extraction, set `AI_API_KEY`, `AI_MODEL`, and optionally `AI_BASE_URL` in the backend environment. Choose a model that supports JSON response format. The backend sends extracted document text to that provider; never put this key in frontend variables. Image OCR requires the Tesseract system executable in addition to the Python package. Text-based PDFs work with the bundled PyMuPDF adapter; scanned PDFs currently receive an actionable unsupported-OCR response.

Analysis and extracted text are sensitive. Configure access, retention, encryption, backups, and provider terms for the intended deployment before using real patient documents.

## Tests and checks

Backend API tests use Python's standard `unittest` runner and FastAPI's test client:

```powershell
cd backend
pip install -r requirements.txt
python -m unittest discover -s tests -p test_api.py -v
```

Frontend production bundle:

```powershell
cd frontend
npm install
npm run build
```

## Deployment

### Render API

The repository includes a root-level `render.yaml`; its pre-deploy command applies `alembic upgrade head` before starting the API. Create a Render web service from that blueprint, configure a PostgreSQL database, and set `DATABASE_URL`, a strong `SECRET_KEY`, `CORS_ORIGINS`, and `DEMO_MODE=false` for a non-demo deployment. Add `AI_API_KEY` only if actual AI processing is desired. Uploaded files use local storage by default; production should point storage to a private durable object store before enabling patient document uploads.

### Netlify client

The repository includes a root-level `netlify.toml` that builds the Vite app from `frontend/`, publishes `frontend/dist`, and routes client-side paths to the SPA entry point. Connect the repository to Netlify and use the detected build settings, or set the base directory to `frontend`, build command to `npm run build`, and publish directory to `dist`.

Set the Netlify environment variable `VITE_API_URL` to `https://<your-render-service>.onrender.com/api` (replace the hostname with your Render service URL). This value is embedded at build time, so redeploy the frontend after changing it. Set the Render environment variable `CORS_ORIGINS` to the deployed Netlify origin, for example `https://<your-site>.netlify.app` (no trailing slash). For a Netlify custom domain, include that origin too; separate multiple origins with commas. Redeploy the API after changing CORS settings.

### Deployment sequence

1. Deploy the Render blueprint in `render.yaml`. It provisions the API and PostgreSQL database. Render prompts for `CORS_ORIGINS`; enter a temporary Netlify origin such as `https://placeholder.netlify.app` for the initial deployment. Confirm `SECRET_KEY` is generated and `DEMO_MODE=false`.
2. Create the Netlify site from this repository and set `VITE_API_URL` to the Render service URL with `/api` appended.
3. Replace the temporary Render `CORS_ORIGINS` value with your actual Netlify origin (and custom domain if applicable), then redeploy the API. Confirm the API health endpoint at `https://<your-render-service>.onrender.com/api/health`, then sign in through the Netlify site.

The application stores uploads on the service filesystem by default. Render's filesystem is ephemeral, so configure private durable object storage before relying on uploaded documents across deploys or restarts. Keep patient data and production AI use disabled until access controls, retention, encryption, backups, monitoring, and provider terms have been reviewed for the intended deployment.

## Security and production readiness

- Passwords use scrypt hashing; API routes use expiring signed JWTs.
- Patients can access their own records. Caregivers must be linked through an invitation and only see tasks assigned to them within a shared journey. Clinical task wording is not editable by caregivers.
- Uploads are type/signature/size checked and are never served without an authenticated ownership check.
- Document confirmation is explicit. AI-proposed tasks remain marked `Needs Verification`.
- The report checklist measures document availability only, never medical readiness.
- External email, SMS, and WhatsApp notifications are not configured or claimed.
- Demo data is fictional. Production use requires a privacy/security review, durable private file storage, operational monitoring and backups, and legal review of applicable Indian DPDP requirements and rules.

## Repository layout

```text
backend/   FastAPI app, models, routers, services, Alembic, tests
frontend/  Vite React app and responsive dashboard
```

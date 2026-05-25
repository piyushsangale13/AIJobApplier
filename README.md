# AI Job Applier

Personal-use AI-powered automatic job application system built as a monorepo with FastAPI, React, PostgreSQL, Playwright, and OpenAI.

This repository now implements a refactored dynamic architecture:

- backend setup
- frontend setup
- PostgreSQL + Alembic setup
- resume upload
- text extraction for PDF/DOCX
- OpenAI structured resume parsing
- dashboard shell and application tracker surface
- dynamic job discovery across LinkedIn, Google, and Wellfound
- ATS detection and routing for Greenhouse, Lever, Workday, and LinkedIn Easy Apply
- AI relevance scoring and auto-queueing pipeline
- background discovery scheduler

## Monorepo Structure

```text
root/
  backend/
  db-init/
  frontend/
  docker/
  docs/
```

## Backend Highlights

- Async FastAPI API with modular structure under `backend/app`
- Async SQLAlchemy session handling
- Alembic migration for initial schema
- Local resume storage under `backend/storage`
- OpenAI integration in `app/services/ai_service.py`
- Structured JSON logging with `structlog`
- Discovery layer under `app/discovery`
- ATS automation layer under `app/automation`
- Scheduler worker under `app/workers`

Key endpoints:

- `GET /health`
- `GET /api/v1/dashboard/stats`
- `GET /api/v1/resumes`
- `POST /api/v1/resumes/upload`
- `GET /api/v1/search-preferences`
- `POST /api/v1/search-preferences`
- `PATCH /api/v1/search-preferences/{id}`
- `GET /api/v1/jobs`
- `POST /api/v1/jobs/discover`
- `POST /api/v1/jobs/discover/preferences`
- `POST /api/v1/jobs/{job_id}/score`
- `GET /api/v1/applications`
- `POST /api/v1/applications/process-queue`

## Frontend Highlights

- React + Vite + TailwindCSS
- React Router app shell
- React Query data fetching
- Resume upload page wired to backend
- Dashboard stats cards
- Application tracker view
- Jobs feed with dynamic discovery, source filters, and ATS visibility

## Local Setup

### 1. Backend

```bash
cd backend
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
uvicorn app.main:app --reload
```

Backend runs on `http://localhost:8000`.

### 2. Frontend

```bash
cd frontend
cp .env.example .env
pnpm install
pnpm dev
```

Frontend runs on `http://localhost:5173`.

### 3. PostgreSQL

Use a local PostgreSQL instance or run Docker Compose:

```bash
cd docker
docker compose up --build
```

Docker Compose now starts services in this order:

1. `postgres`
2. `db-init` runs `db-init/create_default_tables.sql` and `db-init/insert_default_data.sql`
3. `backend`
4. `frontend`

## Environment Variables

Backend: `backend/.env`

```env
APP_NAME=AI Job Applier
ENVIRONMENT=development
API_V1_PREFIX=/api/v1
CORS_ORIGINS=*
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/ai_job_applier
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4.1-mini
REQUEST_TIMEOUT_SECONDS=20
DISCOVERY_SCHEDULER_ENABLED=true
DISCOVERY_INTERVAL_MINUTES=30
AUTO_QUEUE_MIN_SCORE=75
MAX_JOBS_PER_QUERY=20
LINKEDIN_SEARCH_LOCATIONS=India,Bangalore,Hyderabad,Remote India
GOOGLE_SEARCH_DOMAINS=boards.greenhouse.io,jobs.lever.co,workdayjobs.com
WELLFOUND_SEARCH_LOCATIONS=India,Remote
LOG_LEVEL=INFO
```

Frontend: `frontend/.env`

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

## Resume Upload Flow

1. Upload a `.pdf` or `.docx` file from the UI.
2. The backend stores it locally in `backend/storage/resumes/`.
3. Text is extracted with `pypdf` or `python-docx`.
4. OpenAI structured outputs parse:
   - name
   - email
   - skills
   - experience
   - preferred roles
   - projects
   - education
   - keywords
5. The parsed result is saved to PostgreSQL and returned to the client.

If `OPENAI_API_KEY` is not configured, the backend uses a small local fallback parser so the flow still works for development.

## Dynamic Discovery Architecture

Discovery is now split from ATS application handling.

Flow:

1. Discovery sources find jobs dynamically from LinkedIn, Google, and Wellfound
2. The pipeline deduplicates jobs by source id and apply URL
3. `utils/ats_detector.py` detects the real ATS from the apply URL
4. OpenAI scores relevance against the latest or selected resume
5. High-scoring jobs are auto-queued into the applications table
6. ATS handlers process queued applications using Playwright

### Discovery Configuration

Discovery is driven by search preferences and lightweight env defaults:

```env
DISCOVERY_SCHEDULER_ENABLED=true
DISCOVERY_INTERVAL_MINUTES=30
AUTO_QUEUE_MIN_SCORE=75
MAX_JOBS_PER_QUERY=20
LINKEDIN_SEARCH_LOCATIONS=India,Bangalore,Hyderabad,Remote India
GOOGLE_SEARCH_DOMAINS=boards.greenhouse.io,jobs.lever.co,workdayjobs.com
WELLFOUND_SEARCH_LOCATIONS=India,Remote
```

Notes:

- No companies are hardcoded into discovery configuration.
- Google discovery uses search strategies like `site:boards.greenhouse.io "backend engineer India"`.
- LinkedIn and Wellfound discovery generate dynamic search queries from keywords, locations, and experience levels.
- ATS detection is separate from discovery source selection.

### Search Preferences

Use `search_preferences` to store dynamic job search intent:

- `keywords`
- `locations`
- `min_salary_lpa`
- `preferred_companies`
- `enabled`

Enabled preferences are processed by the scheduler every 15-30 minutes.

## Seed Demo Data

```bash
cd backend
python3 scripts/seed_demo.py
```

## Automation Notes

ATS application handlers are implemented for:

- Greenhouse
- Lever
- Workday
- LinkedIn Easy Apply

They use Playwright with:

- persistent browser profiles
- non-headless browser sessions
- retry behavior
- screenshot capture on failure

## Notes

- This is intentionally designed for personal-use automation, not multi-tenant SaaS.
- Authentication is intentionally minimal at this stage.
- Browser automation, Gmail OTP handling, and provider agents will be added in subsequent phases.

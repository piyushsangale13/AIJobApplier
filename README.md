# AI Job Applier

Personal-use AI-powered automatic job application system built as a monorepo with FastAPI, React, PostgreSQL, Playwright, and OpenAI.

This repository currently implements Phase 1:

- backend setup
- frontend setup
- PostgreSQL + Alembic setup
- resume upload
- text extraction for PDF/DOCX
- OpenAI structured resume parsing
- dashboard shell and application tracker surface

## Monorepo Structure

```text
root/
  backend/
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

Key endpoints:

- `GET /health`
- `GET /api/v1/dashboard/stats`
- `GET /api/v1/resumes`
- `POST /api/v1/resumes/upload`
- `GET /api/v1/applications`

## Frontend Highlights

- React + Vite + TailwindCSS
- React Router app shell
- React Query data fetching
- Resume upload page wired to backend
- Dashboard stats cards
- Application tracker view

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

## Environment Variables

Backend: `backend/.env`

```env
APP_NAME=AI Job Applier
ENVIRONMENT=development
API_V1_PREFIX=/api/v1
CORS_ORIGINS=["http://localhost:5173"]
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/ai_job_applier
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4.1-mini
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

## Seed Demo Data

```bash
cd backend
python3 scripts/seed_demo.py
```

## Phase 2 Preview

Next steps in this architecture:

- job provider abstraction and normalized jobs
- LinkedIn, Greenhouse, Lever, and Wellfound discovery
- AI relevance scoring against stored resume data

## Notes

- This is intentionally designed for personal-use automation, not multi-tenant SaaS.
- Authentication is intentionally minimal at this stage.
- Browser automation, Gmail OTP handling, and provider agents will be added in subsequent phases.

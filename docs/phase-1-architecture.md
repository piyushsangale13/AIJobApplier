# Phase 1 Architecture

Phase 1 establishes the local-first base for the personal automation system:

- FastAPI backend with async SQLAlchemy and Alembic
- PostgreSQL persistence for resumes, jobs, applications, users, and browser profiles
- Resume upload pipeline for PDF and DOCX files
- OpenAI-backed structured parsing with a fallback parser for local development
- React + Vite + Tailwind dashboard shell with live dashboard, upload, and tracker views
- Dockerized local development for backend, frontend, and database

Core request flow:

1. Frontend uploads a resume to `POST /api/v1/resumes/upload`
2. Backend stores the file in `backend/storage/resumes`
3. Extracted text is parsed from PDF or DOCX
4. `AIService.parse_resume()` converts raw text into structured JSON
5. Parsed resume is stored in PostgreSQL and returned to the frontend

Phase 2 will add provider-based job discovery and AI scoring against the stored resume data.

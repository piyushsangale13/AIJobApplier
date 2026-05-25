INSERT INTO users (id, email, full_name)
VALUES (
    '11111111-1111-1111-1111-111111111111',
    'demo@example.com',
    'Demo User'
)
ON CONFLICT (email) DO NOTHING;

INSERT INTO jobs (
    id,
    source_id,
    company,
    title,
    location,
    salary_text,
    apply_url,
    ats_type,
    description,
    posted_at,
    relevance_score,
    ai_analysis
)
VALUES (
    '22222222-2222-2222-2222-222222222222',
    'demo-job-001',
    'Example Labs',
    'Backend Engineer',
    'Remote',
    '$140k-$170k',
    'https://example.com/jobs/backend-engineer',
    'greenhouse',
    'Build backend services with Python, FastAPI, and PostgreSQL.',
    NOW(),
    84,
    '{"reasoning": "Seeded demo job for local dashboard validation."}'::jsonb
)
ON CONFLICT (source_id) DO NOTHING;

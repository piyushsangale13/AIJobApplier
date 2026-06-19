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
    source,
    description,
    posted_at,
    discovered_at,
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
    'google',
    'Build backend services with Python, FastAPI, and PostgreSQL.',
    NOW(),
    NOW(),
    84,
    '{"reasoning": "Seeded demo job for local dashboard validation."}'::jsonb
)
ON CONFLICT (source_id) DO NOTHING;

INSERT INTO search_preferences (
    id,
    keywords,
    locations,
    min_salary_lpa,
    preferred_companies,
    enabled,
    label
)
VALUES (
    '33333333-3333-3333-3333-333333333333',
    '["backend engineer", "software engineer", "full stack engineer"]'::jsonb,
    '["India", "Bangalore", "Hyderabad", "Remote India"]'::jsonb,
    18,
    '[]'::jsonb,
    TRUE,
    'India software roles'
)
ON CONFLICT (id) DO NOTHING;

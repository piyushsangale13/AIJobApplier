import asyncio
from datetime import datetime, timezone

from app.db.session import AsyncSessionLocal
from app.models.application import Application
from app.models.job import Job


async def seed() -> None:
    async with AsyncSessionLocal() as session:
        session.add_all(
            [
                Job(
                    company="Example Labs",
                    title="Backend Engineer",
                    location="Remote",
                    salary_text="$140k-$170k",
                    apply_url="https://example.com/jobs/backend-engineer",
                    ats_type="greenhouse",
                    source="google",
                    description="Build API platforms with Python and PostgreSQL.",
                    discovered_at=datetime.now(timezone.utc),
                    relevance_score=84,
                    ai_analysis={"reasoning": "Strong Python match"},
                ),
                Application(
                    company="Example Labs",
                    role="Backend Engineer",
                    status="pending",
                    applied_at=datetime.now(timezone.utc),
                    resume_version="v1",
                    notes="Demo seeded record",
                    screenshots=[],
                ),
            ]
        )
        await session.commit()


if __name__ == "__main__":
    asyncio.run(seed())

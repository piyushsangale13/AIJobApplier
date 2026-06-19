from datetime import date

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.job import Job
from app.schemas.job import JobFilterParams


class JobRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def count_created_today(self) -> int:
        result = await self.session.execute(
            select(func.count()).select_from(Job).where(func.date(Job.created_at) == date.today())
        )
        return int(result.scalar_one())

    def _apply_filters(self, query, filters: JobFilterParams):
        if filters.company:
            query = query.where(Job.company.ilike(f"%{filters.company}%"))
        if filters.location:
            query = query.where(Job.location.ilike(f"%{filters.location}%"))
        if filters.ats_type:
            query = query.where(Job.ats_type == filters.ats_type)
        if filters.source:
            query = query.where(Job.source == filters.source)
        if filters.min_relevance_score is not None:
            query = query.where(Job.relevance_score >= filters.min_relevance_score)
        return query

    async def count_jobs(self, filters: JobFilterParams) -> int:
        query = self._apply_filters(select(func.count()).select_from(Job), filters)
        result = await self.session.execute(query)
        return int(result.scalar_one())

    async def list_jobs(self, filters: JobFilterParams, page: int = 1, page_size: int = 20) -> list[Job]:
        offset = (page - 1) * page_size
        query = (
            self._apply_filters(select(Job), filters)
            .order_by(Job.created_at.desc())
            .limit(page_size)
            .offset(offset)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_id(self, job_id: str) -> Job | None:
        result = await self.session.execute(select(Job).where(Job.id == job_id))
        return result.scalar_one_or_none()

    async def get_by_source_id(self, source_id: str) -> Job | None:
        result = await self.session.execute(select(Job).where(Job.source_id == source_id))
        return result.scalar_one_or_none()

    async def get_by_apply_url(self, apply_url: str) -> Job | None:
        result = await self.session.execute(select(Job).where(Job.apply_url == apply_url))
        return result.scalar_one_or_none()

    async def update_score(self, job_id: str, score: float, ai_analysis: dict) -> Job:
        job = await self.get_by_id(job_id)
        if not job:
            raise LookupError("Job not found.")
        job.relevance_score = score
        job.ai_analysis = ai_analysis
        await self.session.commit()
        await self.session.refresh(job)
        return job

    async def upsert_job(self, payload: dict) -> Job:
        existing = None
        if payload.get("source_id"):
            existing = await self.get_by_source_id(payload["source_id"])
        if not existing:
            existing = await self.get_by_apply_url(payload["apply_url"])
        if existing:
            for key, value in payload.items():
                setattr(existing, key, value)
            await self.session.commit()
            await self.session.refresh(existing)
            return existing

        job = Job(**payload)
        self.session.add(job)
        await self.session.commit()
        await self.session.refresh(job)
        return job

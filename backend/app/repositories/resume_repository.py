from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.resume import Resume


class ResumeRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, resume: Resume) -> Resume:
        self.session.add(resume)
        await self.session.commit()
        await self.session.refresh(resume)
        return resume

    async def list_all(self) -> list[Resume]:
        result = await self.session.execute(select(Resume).order_by(Resume.created_at.desc()))
        return list(result.scalars().all())

    async def get_latest(self) -> Resume | None:
        result = await self.session.execute(select(Resume).order_by(Resume.created_at.desc()).limit(1))
        return result.scalar_one_or_none()

    async def get_by_id(self, resume_id: str) -> Resume | None:
        result = await self.session.execute(select(Resume).where(Resume.id == resume_id))
        return result.scalar_one_or_none()

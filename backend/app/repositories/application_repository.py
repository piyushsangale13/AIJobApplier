from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.application import Application


class ApplicationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_all(self) -> list[Application]:
        result = await self.session.execute(
            select(Application).order_by(Application.created_at.desc())
        )
        return list(result.scalars().all())

    async def count_by_status(self, status: str) -> int:
        result = await self.session.execute(
            select(func.count()).select_from(Application).where(Application.status == status)
        )
        return int(result.scalar_one())

    async def get_by_job_id(self, job_id: str) -> Application | None:
        result = await self.session.execute(select(Application).where(Application.job_id == job_id))
        return result.scalar_one_or_none()

    async def create_or_update_for_job(self, payload: dict) -> Application:
        existing = None
        if payload.get("job_id"):
            existing = await self.get_by_job_id(payload["job_id"])
        if existing:
            if existing.status in {"applying", "applied"} and payload.get("status") == "pending":
                return existing
            for key, value in payload.items():
                setattr(existing, key, value)
            await self.session.commit()
            await self.session.refresh(existing)
            return existing

        item = Application(**payload)
        self.session.add(item)
        await self.session.commit()
        await self.session.refresh(item)
        return item

    async def list_pending(self, limit: int = 25) -> list[Application]:
        result = await self.session.execute(
            select(Application)
            .where(Application.status == "pending")
            .order_by(Application.created_at.asc())
            .limit(limit)
        )
        return list(result.scalars().all())

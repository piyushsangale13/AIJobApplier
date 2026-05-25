from datetime import date

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.job import Job


class JobRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def count_created_today(self) -> int:
        result = await self.session.execute(
            select(func.count()).select_from(Job).where(func.date(Job.created_at) == date.today())
        )
        return int(result.scalar_one())

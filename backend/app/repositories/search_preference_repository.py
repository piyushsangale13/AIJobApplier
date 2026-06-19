from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.search_preference import SearchPreference


class SearchPreferenceRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_all(self, enabled_only: bool = False) -> list[SearchPreference]:
        query = select(SearchPreference).order_by(SearchPreference.created_at.desc())
        if enabled_only:
            query = query.where(SearchPreference.enabled.is_(True))
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_id(self, preference_id: str) -> SearchPreference | None:
        result = await self.session.execute(
            select(SearchPreference).where(SearchPreference.id == preference_id)
        )
        return result.scalar_one_or_none()

    async def create(self, payload: dict) -> SearchPreference:
        item = SearchPreference(**payload)
        self.session.add(item)
        await self.session.commit()
        await self.session.refresh(item)
        return item

    async def update(self, item: SearchPreference, updates: dict) -> SearchPreference:
        for key, value in updates.items():
            setattr(item, key, value)
        await self.session.commit()
        await self.session.refresh(item)
        return item

from fastapi import HTTPException, status

from app.repositories.search_preference_repository import SearchPreferenceRepository
from app.schemas.search_preference import (
    SearchPreferenceCreate,
    SearchPreferenceRead,
    SearchPreferenceUpdate,
)


class SearchPreferenceService:
    def __init__(self, repository: SearchPreferenceRepository) -> None:
        self.repository = repository

    async def list_preferences(self, enabled_only: bool = False) -> list[SearchPreferenceRead]:
        items = await self.repository.list_all(enabled_only=enabled_only)
        return [SearchPreferenceRead.model_validate(item) for item in items]

    async def create_preference(self, payload: SearchPreferenceCreate) -> SearchPreferenceRead:
        item = await self.repository.create(payload.model_dump())
        return SearchPreferenceRead.model_validate(item)

    async def update_preference(
        self, preference_id: str, payload: SearchPreferenceUpdate
    ) -> SearchPreferenceRead:
        item = await self.repository.get_by_id(preference_id)
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Search preference not found.")
        updates = payload.model_dump(exclude_unset=True)
        item = await self.repository.update(item, updates)
        return SearchPreferenceRead.model_validate(item)

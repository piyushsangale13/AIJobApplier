from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_session
from app.repositories.search_preference_repository import SearchPreferenceRepository
from app.schemas.search_preference import (
    SearchPreferenceCreate,
    SearchPreferenceRead,
    SearchPreferenceUpdate,
)
from app.services.search_preference_service import SearchPreferenceService


router = APIRouter()


@router.get("", response_model=list[SearchPreferenceRead])
async def list_preferences(session: AsyncSession = Depends(get_session)) -> list[SearchPreferenceRead]:
    service = SearchPreferenceService(SearchPreferenceRepository(session))
    return await service.list_preferences()


@router.post("", response_model=SearchPreferenceRead)
async def create_preference(
    payload: SearchPreferenceCreate,
    session: AsyncSession = Depends(get_session),
) -> SearchPreferenceRead:
    service = SearchPreferenceService(SearchPreferenceRepository(session))
    return await service.create_preference(payload)


@router.patch("/{preference_id}", response_model=SearchPreferenceRead)
async def update_preference(
    preference_id: str,
    payload: SearchPreferenceUpdate,
    session: AsyncSession = Depends(get_session),
) -> SearchPreferenceRead:
    service = SearchPreferenceService(SearchPreferenceRepository(session))
    return await service.update_preference(preference_id, payload)

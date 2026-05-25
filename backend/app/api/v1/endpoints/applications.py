from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_session
from app.repositories.application_repository import ApplicationRepository
from app.schemas.application import ApplicationRead


router = APIRouter()


@router.get("", response_model=list[ApplicationRead])
async def list_applications(session: AsyncSession = Depends(get_session)) -> list[ApplicationRead]:
    repository = ApplicationRepository(session)
    applications = await repository.list_all()
    return [ApplicationRead.model_validate(item) for item in applications]

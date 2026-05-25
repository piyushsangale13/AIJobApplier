from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_session
from app.repositories.application_repository import ApplicationRepository
from app.repositories.job_repository import JobRepository
from app.repositories.resume_repository import ResumeRepository
from app.schemas.application import ApplicationRead
from app.services.application_service import ApplicationService


router = APIRouter()


@router.get("", response_model=list[ApplicationRead])
async def list_applications(session: AsyncSession = Depends(get_session)) -> list[ApplicationRead]:
    service = ApplicationService(
        application_repository=ApplicationRepository(session),
        job_repository=JobRepository(session),
        resume_repository=ResumeRepository(session),
    )
    return await service.list_applications()


@router.post("/process-queue", response_model=list[ApplicationRead])
async def process_queue(session: AsyncSession = Depends(get_session)) -> list[ApplicationRead]:
    service = ApplicationService(
        application_repository=ApplicationRepository(session),
        job_repository=JobRepository(session),
        resume_repository=ResumeRepository(session),
    )
    return await service.process_pending_queue()

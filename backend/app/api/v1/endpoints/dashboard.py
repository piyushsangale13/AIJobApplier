from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_session
from app.repositories.application_repository import ApplicationRepository
from app.repositories.job_repository import JobRepository
from app.schemas.dashboard import DashboardStats
from app.services.dashboard_service import DashboardService


router = APIRouter()


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(session: AsyncSession = Depends(get_session)) -> DashboardStats:
    service = DashboardService(
        job_repository=JobRepository(session),
        application_repository=ApplicationRepository(session),
    )
    return await service.get_stats()

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_session
from app.repositories.application_repository import ApplicationRepository
from app.repositories.job_repository import JobRepository
from app.repositories.resume_repository import ResumeRepository
from app.repositories.search_preference_repository import SearchPreferenceRepository
from app.schemas.job import (
    JobDiscoveryRequest,
    JobDiscoveryResponse,
    JobFilterParams,
    JobRead,
    JobScoreResponse,
)
from app.services.job_pipeline import JobPipelineService


router = APIRouter()


@router.get("", response_model=list[JobRead])
async def list_jobs(
    company: str | None = Query(default=None),
    location: str | None = Query(default=None),
    ats_type: str | None = Query(default=None),
    source: str | None = Query(default=None),
    min_relevance_score: float | None = Query(default=None),
    session: AsyncSession = Depends(get_session),
) -> list[JobRead]:
    repository = JobRepository(session)
    jobs = await repository.list_jobs(
        JobFilterParams(
            company=company,
            location=location,
            ats_type=ats_type,
            source=source,
            min_relevance_score=min_relevance_score,
        )
    )
    return [JobRead.model_validate(job) for job in jobs]


@router.post("/discover", response_model=JobDiscoveryResponse)
async def discover_jobs(
    payload: JobDiscoveryRequest,
    session: AsyncSession = Depends(get_session),
) -> JobDiscoveryResponse:
    service = JobPipelineService(
        job_repository=JobRepository(session),
        resume_repository=ResumeRepository(session),
        search_preference_repository=SearchPreferenceRepository(session),
        application_repository=ApplicationRepository(session),
    )
    try:
        return await service.discover_from_request(payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/discover/preferences", response_model=list[JobDiscoveryResponse])
async def discover_from_preferences(
    session: AsyncSession = Depends(get_session),
) -> list[JobDiscoveryResponse]:
    service = JobPipelineService(
        job_repository=JobRepository(session),
        resume_repository=ResumeRepository(session),
        search_preference_repository=SearchPreferenceRepository(session),
        application_repository=ApplicationRepository(session),
    )
    return await service.discover_from_preferences()


@router.post("/{job_id}/score", response_model=JobScoreResponse)
async def rescore_job(
    job_id: str,
    resume_id: str | None = Query(default=None),
    session: AsyncSession = Depends(get_session),
) -> JobScoreResponse:
    service = JobPipelineService(
        job_repository=JobRepository(session),
        resume_repository=ResumeRepository(session),
        search_preference_repository=SearchPreferenceRepository(session),
        application_repository=ApplicationRepository(session),
    )
    try:
        return await service.rescore_job(job_id, resume_id=resume_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

import math

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_session
from app.repositories.job_repository import JobRepository
from app.repositories.resume_repository import ResumeRepository
from app.repositories.search_preference_repository import SearchPreferenceRepository
from app.schemas.job import (
    CoverLetterResponse,
    JobDiscoveryRequest,
    JobDiscoveryResponse,
    JobFilterParams,
    JobRead,
    JobScoreResponse,
    JobsPage,
    TailoredResumeResponse,
)
from app.services.ai_service import AIService
from app.services.job_pipeline import JobPipelineService


router = APIRouter()


def _build_pipeline(session: AsyncSession) -> JobPipelineService:
    return JobPipelineService(
        job_repository=JobRepository(session),
        resume_repository=ResumeRepository(session),
        search_preference_repository=SearchPreferenceRepository(session),
    )


@router.get("", response_model=JobsPage)
async def list_jobs(
    company: str | None = Query(default=None),
    location: str | None = Query(default=None),
    ats_type: str | None = Query(default=None),
    source: str | None = Query(default=None),
    min_relevance_score: float | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
) -> JobsPage:
    repository = JobRepository(session)
    filters = JobFilterParams(
        company=company,
        location=location,
        ats_type=ats_type,
        source=source,
        min_relevance_score=min_relevance_score,
    )
    total = await repository.count_jobs(filters)
    jobs = await repository.list_jobs(filters, page=page, page_size=page_size)
    return JobsPage(
        items=[JobRead.model_validate(job) for job in jobs],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=max(1, math.ceil(total / page_size)),
    )


@router.post("/discover", response_model=JobDiscoveryResponse)
async def discover_jobs(
    payload: JobDiscoveryRequest,
    session: AsyncSession = Depends(get_session),
) -> JobDiscoveryResponse:
    try:
        return await _build_pipeline(session).discover_from_request(payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/discover/preferences", response_model=list[JobDiscoveryResponse])
async def discover_from_preferences(
    session: AsyncSession = Depends(get_session),
) -> list[JobDiscoveryResponse]:
    return await _build_pipeline(session).discover_from_preferences()


@router.post("/{job_id}/score", response_model=JobScoreResponse)
async def rescore_job(
    job_id: str,
    resume_id: str | None = Query(default=None),
    session: AsyncSession = Depends(get_session),
) -> JobScoreResponse:
    try:
        return await _build_pipeline(session).rescore_job(job_id, resume_id=resume_id)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/{job_id}/cover-letter", response_model=CoverLetterResponse)
async def generate_cover_letter(
    job_id: str,
    resume_id: str | None = Query(default=None),
    session: AsyncSession = Depends(get_session),
) -> CoverLetterResponse:
    job_repo = JobRepository(session)
    resume_repo = ResumeRepository(session)

    job = await job_repo.get_by_id(job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found.")

    resume = await resume_repo.get_by_id(resume_id) if resume_id else await resume_repo.get_latest()
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No resume found. Upload a resume first.",
        )

    cover_letter = await AIService().generate_cover_letter(resume.parsed_data, job.description)
    return CoverLetterResponse(cover_letter=cover_letter)


@router.post("/{job_id}/tailor-resume", response_model=TailoredResumeResponse)
async def tailor_resume(
    job_id: str,
    resume_id: str | None = Query(default=None),
    session: AsyncSession = Depends(get_session),
) -> TailoredResumeResponse:
    job_repo = JobRepository(session)
    resume_repo = ResumeRepository(session)

    job = await job_repo.get_by_id(job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found.")

    resume = await resume_repo.get_by_id(resume_id) if resume_id else await resume_repo.get_latest()
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No resume found. Upload a resume first.",
        )

    result = await AIService().tailor_resume(resume.parsed_data, job.description)
    return TailoredResumeResponse(
        tailored_resume=result.tailored_resume,
        key_changes=result.key_changes,
        matched_keywords=result.matched_keywords,
    )

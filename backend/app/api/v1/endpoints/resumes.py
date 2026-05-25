from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_session
from app.repositories.resume_repository import ResumeRepository
from app.schemas.resume import ResumeRead, ResumeUploadResponse
from app.services.resume_service import ResumeService


router = APIRouter()


@router.post("/upload", response_model=ResumeUploadResponse)
async def upload_resume(
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session),
) -> ResumeUploadResponse:
    service = ResumeService(repository=ResumeRepository(session))
    resume = await service.upload_and_parse(file)
    return ResumeUploadResponse(resume=ResumeRead.model_validate(resume))


@router.get("", response_model=list[ResumeRead])
async def list_resumes(session: AsyncSession = Depends(get_session)) -> list[ResumeRead]:
    service = ResumeService(repository=ResumeRepository(session))
    resumes = await service.list_resumes()
    return [ResumeRead.model_validate(resume) for resume in resumes]

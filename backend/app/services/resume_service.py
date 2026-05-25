from pathlib import Path

from fastapi import HTTPException, UploadFile, status

from app.models.resume import Resume
from app.repositories.resume_repository import ResumeRepository
from app.schemas.resume import ResumeParsedData
from app.services.ai_service import AIService
from app.services.document_parser import DocumentParser
from app.services.file_storage import FileStorageService


class ResumeService:
    SUPPORTED_EXTENSIONS = {".pdf", ".docx"}

    def __init__(
        self,
        repository: ResumeRepository,
        file_storage: FileStorageService | None = None,
        document_parser: DocumentParser | None = None,
        ai_service: AIService | None = None,
    ) -> None:
        self.repository = repository
        self.file_storage = file_storage or FileStorageService()
        self.document_parser = document_parser or DocumentParser()
        self.ai_service = ai_service or AIService()

    async def upload_and_parse(self, upload: UploadFile) -> Resume:
        extension = Path(upload.filename or "").suffix.lower()
        if extension not in self.SUPPORTED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PDF and DOCX resumes are supported.",
            )

        saved_path = await self.file_storage.save_resume(upload)
        raw_text = await self.document_parser.extract_text(saved_path)
        if not raw_text.strip():
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Failed to extract any text from resume.",
            )

        parsed_data: ResumeParsedData = await self.ai_service.parse_resume(raw_text)
        resume = Resume(
            filename=Path(saved_path).name,
            file_path=str(saved_path),
            file_type=extension.lstrip("."),
            raw_text=raw_text,
            parsed_data=parsed_data.model_dump(mode="json"),
            summary=parsed_data.summary,
        )
        return await self.repository.create(resume)

    async def list_resumes(self) -> list[Resume]:
        return await self.repository.list_all()

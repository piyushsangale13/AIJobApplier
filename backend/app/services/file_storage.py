from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from app.core.config import get_settings


class FileStorageService:
    def __init__(self) -> None:
        self.settings = get_settings()

    async def save_resume(self, upload: UploadFile) -> Path:
        extension = Path(upload.filename or "").suffix.lower()
        filename = f"{uuid4()}{extension}"
        destination = self.settings.resume_upload_path / filename
        content = await upload.read()
        destination.write_bytes(content)
        await upload.close()
        return destination

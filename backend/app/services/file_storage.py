import io
from pathlib import Path
from uuid import uuid4

from minio import Minio

from app.core.config import get_settings


class FileStorageService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.client = Minio(
            self.settings.minio_endpoint,
            access_key=self.settings.minio_access_key,
            secret_key=self.settings.minio_secret_key,
            secure=self.settings.minio_secure,
        )
        self._ensure_bucket()

    def _ensure_bucket(self) -> None:
        if not self.client.bucket_exists(self.settings.minio_bucket):
            self.client.make_bucket(self.settings.minio_bucket)

    async def save_resume(self, content: bytes, filename: str) -> str:
        extension = Path(filename).suffix.lower()
        object_name = f"{uuid4()}{extension}"
        content_type = (
            "application/pdf"
            if extension == ".pdf"
            else "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        self.client.put_object(
            self.settings.minio_bucket,
            object_name,
            io.BytesIO(content),
            length=len(content),
            content_type=content_type,
        )
        return object_name

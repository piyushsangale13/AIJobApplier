import asyncio
import io
from pathlib import Path
from uuid import uuid4

from minio import Minio

from app.core.config import get_settings


class FileStorageService:
    def __init__(self) -> None:
        settings = get_settings()
        self._bucket = settings.minio_bucket
        self._client = Minio(
            settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=settings.minio_secure,
        )

    def _ensure_bucket_sync(self) -> None:
        if not self._client.bucket_exists(self._bucket):
            self._client.make_bucket(self._bucket)

    async def save_resume(self, content: bytes, filename: str) -> str:
        extension = Path(filename).suffix.lower()
        object_name = f"{uuid4()}{extension}"
        content_type = (
            "application/pdf"
            if extension == ".pdf"
            else "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

        def _upload() -> None:
            self._ensure_bucket_sync()
            self._client.put_object(
                self._bucket,
                object_name,
                io.BytesIO(content),
                length=len(content),
                content_type=content_type,
            )

        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, _upload)
        return object_name

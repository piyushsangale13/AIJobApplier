from datetime import datetime

from app.schemas.common import TimestampedSchema


class ApplicationRead(TimestampedSchema):
    company: str
    role: str
    status: str
    applied_at: datetime | None
    resume_version: str | None
    notes: str | None
    screenshots: list

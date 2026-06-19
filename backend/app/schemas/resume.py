from pydantic import BaseModel, EmailStr, Field

from app.schemas.common import TimestampedSchema


class ResumeParsedData(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    skills: list[str] = Field(default_factory=list)
    experience: list[str] = Field(default_factory=list)
    preferred_roles: list[str] = Field(default_factory=list)
    projects: list[str] = Field(default_factory=list)
    education: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
    summary: str | None = None


class ResumeRead(TimestampedSchema):
    filename: str
    file_path: str
    file_type: str
    raw_text: str
    parsed_data: dict
    summary: str | None = None
    ats_score: int | None = None
    ats_analysis: dict = {}


class ResumeUploadResponse(BaseModel):
    resume: ResumeRead

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, HttpUrl

from app.schemas.common import TimestampedSchema


DiscoverySourceName = Literal["linkedin", "google", "wellfound"]


class JobRead(TimestampedSchema):
    source_id: str | None
    company: str
    title: str
    location: str | None
    salary_text: str | None
    apply_url: str
    ats_type: str
    source: str
    description: str
    posted_at: datetime | None
    discovered_at: datetime
    relevance_score: float | None
    ai_analysis: dict


class JobDiscoveryRequest(BaseModel):
    keywords: list[str] = Field(default_factory=list)
    locations: list[str] = Field(default_factory=list)
    experience_levels: list[str] = Field(default_factory=list)
    sources: list[DiscoverySourceName] = Field(default_factory=list)
    resume_id: str | None = None
    limit_per_source: int = Field(default=10, ge=1, le=50)
    remote_only: bool = False


class JobScoreResponse(BaseModel):
    relevance_score: int = Field(ge=1, le=100)
    missing_skills: list[str] = Field(default_factory=list)
    reasoning: str


class TailoredResumeResponse(BaseModel):
    tailored_resume: str
    key_changes: list[str] = Field(default_factory=list)
    matched_keywords: list[str] = Field(default_factory=list)


class JobDiscoveryResponse(BaseModel):
    jobs: list[JobRead]
    source_counts: dict[str, int]
    used_resume_id: str | None = None


class JobFilterParams(BaseModel):
    company: str | None = None
    location: str | None = None
    ats_type: str | None = None
    source: str | None = None
    min_relevance_score: float | None = Field(default=None, ge=0, le=100)


class JobsPage(BaseModel):
    items: list[JobRead]
    total: int
    page: int
    page_size: int
    total_pages: int


class DiscoveredJob(BaseModel):
    source_id: str
    company: str
    title: str
    location: str | None = None
    salary_text: str | None = None
    apply_url: HttpUrl
    description: str
    posted_at: datetime | None = None
    source: DiscoverySourceName
    metadata: dict = Field(default_factory=dict)

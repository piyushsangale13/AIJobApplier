from pydantic import BaseModel, Field

from app.schemas.common import TimestampedSchema


class SearchPreferenceCreate(BaseModel):
    keywords: list[str] = Field(default_factory=list)
    locations: list[str] = Field(default_factory=list)
    min_salary_lpa: float | None = None
    preferred_companies: list[str] = Field(default_factory=list)
    enabled: bool = True
    label: str | None = None


class SearchPreferenceUpdate(BaseModel):
    keywords: list[str] | None = None
    locations: list[str] | None = None
    min_salary_lpa: float | None = None
    preferred_companies: list[str] | None = None
    enabled: bool | None = None
    label: str | None = None


class SearchPreferenceRead(TimestampedSchema):
    keywords: list[str]
    locations: list[str]
    min_salary_lpa: float | None
    preferred_companies: list[str]
    enabled: bool
    label: str | None

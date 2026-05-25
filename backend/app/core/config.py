from functools import lru_cache
from pathlib import Path
from typing import Annotated

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "AI Job Applier"
    environment: str = "development"
    api_v1_prefix: str = "/api/v1"
    cors_origins: str = "*"

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/ai_job_applier"
    openai_api_key: str = ""
    openai_model: str = "gpt-4.1-mini"
    request_timeout_seconds: float = 20.0
    discovery_scheduler_enabled: bool = True
    discovery_interval_minutes: int = 30
    auto_queue_min_score: int = 75
    max_jobs_per_query: int = 20

    linkedin_search_locations: Annotated[list[str], NoDecode] = Field(
        default_factory=lambda: ["India", "Bangalore", "Hyderabad", "Remote India"]
    )
    google_search_domains: Annotated[list[str], NoDecode] = Field(
        default_factory=lambda: ["boards.greenhouse.io", "jobs.lever.co", "workdayjobs.com"]
    )
    wellfound_search_locations: Annotated[list[str], NoDecode] = Field(
        default_factory=lambda: ["India", "Remote"]
    )

    storage_path: Path = BASE_DIR / "storage"
    resume_upload_path: Path = BASE_DIR / "storage" / "resumes"
    screenshot_path: Path = BASE_DIR / "storage" / "screenshots"
    log_level: str = "INFO"

    @field_validator(
        "linkedin_search_locations",
        "google_search_domains",
        "wellfound_search_locations",
        mode="before",
    )
    @classmethod
    def parse_csv_list(cls, value: object) -> object:
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.storage_path.mkdir(parents=True, exist_ok=True)
    settings.resume_upload_path.mkdir(parents=True, exist_ok=True)
    settings.screenshot_path.mkdir(parents=True, exist_ok=True)
    return settings

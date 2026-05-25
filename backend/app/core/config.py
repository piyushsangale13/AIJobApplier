from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


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
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:5173"])

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/ai_job_applier"
    openai_api_key: str = ""
    openai_model: str = "gpt-4.1-mini"

    storage_path: Path = BASE_DIR / "storage"
    resume_upload_path: Path = BASE_DIR / "storage" / "resumes"
    screenshot_path: Path = BASE_DIR / "storage" / "screenshots"
    log_level: str = "INFO"


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.storage_path.mkdir(parents=True, exist_ok=True)
    settings.resume_upload_path.mkdir(parents=True, exist_ok=True)
    settings.screenshot_path.mkdir(parents=True, exist_ok=True)
    return settings

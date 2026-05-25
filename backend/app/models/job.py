from datetime import datetime

from sqlalchemy import DateTime, Float, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class Job(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "jobs"

    source_id: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    company: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    salary_text: Mapped[str | None] = mapped_column(String(255), nullable=True)
    apply_url: Mapped[str] = mapped_column(String(2048), nullable=False)
    ats_type: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    posted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    relevance_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    ai_analysis: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    applications = relationship("Application", back_populates="job")

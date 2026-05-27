from sqlalchemy import ForeignKey, SmallInteger, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class Resume(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "resumes"

    user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    file_type: Mapped[str] = mapped_column(String(50), nullable=False)
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    parsed_data: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    ats_score: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    ats_analysis: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    user = relationship("User", back_populates="resumes")
    applications = relationship("Application", back_populates="resume")

from sqlalchemy import Boolean, Float, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class SearchPreference(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "search_preferences"

    keywords: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    locations: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    min_salary_lpa: Mapped[float | None] = mapped_column(Float, nullable=True)
    preferred_companies: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    label: Mapped[str | None] = mapped_column(String(255), nullable=True)

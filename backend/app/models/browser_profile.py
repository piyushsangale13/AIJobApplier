from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class BrowserProfile(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "browser_profiles"

    user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    profile_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    profile_metadata: Mapped[dict] = mapped_column("metadata", JSONB, nullable=False, default=dict)

    user = relationship("User", back_populates="browser_profiles")

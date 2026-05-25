"""dynamic discovery refactor

Revision ID: 20260526_000002
Revises: 20260525_000001
Create Date: 2026-05-26 00:00:02
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "20260526_000002"
down_revision: str | None = "20260525_000001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("jobs", sa.Column("source", sa.String(length=100), nullable=True))
    op.add_column("jobs", sa.Column("discovered_at", sa.DateTime(timezone=True), nullable=True))
    op.execute("UPDATE jobs SET source = 'google' WHERE source IS NULL")
    op.execute("UPDATE jobs SET discovered_at = COALESCE(posted_at, created_at, now()) WHERE discovered_at IS NULL")
    op.alter_column("jobs", "source", nullable=False)
    op.alter_column("jobs", "discovered_at", nullable=False)
    op.create_index(op.f("ix_jobs_source"), "jobs", ["source"], unique=False)

    op.create_table(
        "search_preferences",
        sa.Column("keywords", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("locations", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("min_salary_lpa", sa.Float(), nullable=True),
        sa.Column("preferred_companies", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("label", sa.String(length=255), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("search_preferences")
    op.drop_index(op.f("ix_jobs_source"), table_name="jobs")
    op.drop_column("jobs", "discovered_at")
    op.drop_column("jobs", "source")

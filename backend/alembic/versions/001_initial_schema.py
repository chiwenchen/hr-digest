"""initial schema

Revision ID: 001
Revises:
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # users table
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("role", sa.String(20), nullable=False, server_default="hr"),
        sa.Column("email_subscribed", sa.Boolean(), nullable=True, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )

    # digests table
    op.create_table(
        "digests",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("month", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="draft"),
        sa.Column("published_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("year", "month", name="uq_digest_year_month"),
    )

    # law_changes table
    op.create_table(
        "law_changes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("digest_id", sa.Integer(), nullable=False),
        sa.Column("law_name", sa.String(100), nullable=False),
        sa.Column("article_number", sa.String(20), nullable=False),
        sa.Column("change_summary", sa.Text(), nullable=False),
        sa.Column("action_items", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["digest_id"], ["digests.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    # news_candidates table
    op.create_table(
        "news_candidates",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("digest_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("source", sa.String(100), nullable=False),
        sa.Column("url", sa.String(1000), nullable=False),
        sa.Column("published_date", sa.Date(), nullable=False),
        sa.Column("ai_summary", sa.Text(), nullable=True),
        sa.Column("ai_action", sa.Text(), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=True),
        sa.Column("is_approved", sa.Boolean(), nullable=True, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["digest_id"], ["digests.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    # hr_calendar table
    op.create_table(
        "hr_calendar",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("month", sa.Integer(), nullable=False),
        sa.Column("quarter", sa.Integer(), nullable=True),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
    )

    # bills table
    op.create_table(
        "bills",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("status", sa.String(50), nullable=False, server_default="tracking"),
        sa.Column("source_url", sa.String(1000), nullable=True),
        sa.Column("current_stage", sa.String(200), nullable=True),
        sa.Column("expected_timeline", sa.String(200), nullable=True),
        sa.Column("impact_summary", sa.Text(), nullable=True),
        sa.Column("hr_preparation", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True, server_default=sa.text("true")),
        sa.Column("last_updated", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("bills")
    op.drop_table("hr_calendar")
    op.drop_table("news_candidates")
    op.drop_table("law_changes")
    op.drop_table("digests")
    op.drop_table("users")

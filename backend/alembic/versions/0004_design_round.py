"""Design round: design_prompts, design_sessions

Revision ID: 0004
Revises: 0003
Create Date: 2026-07-08

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0004"
down_revision: Union[str, None] = "0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

JSONVariant = sa.JSON().with_variant(postgresql.JSONB(), "postgresql")


def upgrade() -> None:
    op.create_table(
        "design_prompts",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("difficulty", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("prompt_md", sa.String(), nullable=False),
        sa.Column("rubric_md", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "design_sessions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("prompt_id", sa.Uuid(), nullable=False),
        sa.Column("duration_s", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("transcript", JSONVariant, nullable=False),
        sa.Column("grade", JSONVariant, nullable=True),
        sa.Column("overall_score", sa.Float(), nullable=True),
        sa.Column("elo_delta", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("graded_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["prompt_id"], ["design_prompts.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_design_sessions_user_id"), "design_sessions", ["user_id"], unique=False
    )
    op.create_index(
        op.f("ix_design_sessions_created_at"), "design_sessions", ["created_at"], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_design_sessions_created_at"), table_name="design_sessions")
    op.drop_index(op.f("ix_design_sessions_user_id"), table_name="design_sessions")
    op.drop_table("design_sessions")

    op.drop_table("design_prompts")

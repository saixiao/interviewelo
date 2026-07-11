"""Approach round: approach_prompts, approach_sessions, approach_answers

Revision ID: 0003
Revises: 0002
Create Date: 2026-07-07

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

JSONVariant = sa.JSON().with_variant(postgresql.JSONB(), "postgresql")


def upgrade() -> None:
    op.create_table(
        "approach_prompts",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("difficulty", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("prompt_md", sa.String(), nullable=False),
        sa.Column("grading_notes_md", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "approach_sessions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("elapsed_s", sa.Float(), nullable=False),
        sa.Column("overall_score", sa.Float(), nullable=False),
        sa.Column("session_summary", sa.String(), nullable=False),
        sa.Column("elo_delta", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_approach_sessions_user_id"), "approach_sessions", ["user_id"], unique=False
    )
    op.create_index(
        op.f("ix_approach_sessions_created_at"), "approach_sessions", ["created_at"], unique=False
    )

    op.create_table(
        "approach_answers",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("session_id", sa.Uuid(), nullable=False),
        sa.Column("prompt_id", sa.Uuid(), nullable=False),
        sa.Column("answer_text", sa.String(), nullable=False),
        sa.Column("grade", JSONVariant, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["session_id"], ["approach_sessions.id"]),
        sa.ForeignKeyConstraint(["prompt_id"], ["approach_prompts.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_approach_answers_session_id"), "approach_answers", ["session_id"], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_approach_answers_session_id"), table_name="approach_answers")
    op.drop_table("approach_answers")

    op.drop_index(op.f("ix_approach_sessions_created_at"), table_name="approach_sessions")
    op.drop_index(op.f("ix_approach_sessions_user_id"), table_name="approach_sessions")
    op.drop_table("approach_sessions")

    op.drop_table("approach_prompts")

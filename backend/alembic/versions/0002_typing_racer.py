"""Typing Racer: typing_snippets, typing_attempts

Revision ID: 0002
Revises: 0001
Create Date: 2026-07-05

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

JSONVariant = sa.JSON().with_variant(postgresql.JSONB(), "postgresql")


def upgrade() -> None:
    op.create_table(
        "typing_snippets",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("language", sa.String(length=20), nullable=False),
        sa.Column("difficulty", sa.Integer(), nullable=False),
        sa.Column("content", sa.String(), nullable=False),
        sa.Column("char_count", sa.Integer(), nullable=False),
        sa.Column("line_count", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "typing_attempts",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("mode", sa.String(length=20), nullable=False),
        sa.Column("duration_s", sa.Integer(), nullable=False),
        sa.Column("elapsed_s", sa.Float(), nullable=False),
        sa.Column("raw_wpm", sa.Float(), nullable=True),
        sa.Column("accuracy", sa.Float(), nullable=True),
        sa.Column("lines_correct", sa.Integer(), nullable=True),
        sa.Column("lines_total", sa.Integer(), nullable=True),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column("elo_delta", sa.Integer(), nullable=False),
        sa.Column("input_log", JSONVariant, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_typing_attempts_user_id"), "typing_attempts", ["user_id"], unique=False)
    op.create_index(
        op.f("ix_typing_attempts_created_at"), "typing_attempts", ["created_at"], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_typing_attempts_created_at"), table_name="typing_attempts")
    op.drop_index(op.f("ix_typing_attempts_user_id"), table_name="typing_attempts")
    op.drop_table("typing_attempts")
    op.drop_table("typing_snippets")

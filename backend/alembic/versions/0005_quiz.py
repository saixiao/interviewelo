"""Quiz modes: quiz_questions, quiz_sessions, quiz_answers

Revision ID: 0005
Revises: 0004
Create Date: 2026-07-10

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0005"
down_revision: Union[str, None] = "0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

JSONVariant = sa.JSON().with_variant(postgresql.JSONB(), "postgresql")


def upgrade() -> None:
    op.create_table(
        "quiz_questions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("category", sa.String(length=20), nullable=False),
        sa.Column("topic", sa.String(length=50), nullable=True),
        sa.Column("difficulty", sa.Integer(), nullable=False),
        sa.Column("prompt_md", sa.String(), nullable=False),
        sa.Column("code_snippet", sa.String(), nullable=True),
        sa.Column("language", sa.String(length=20), nullable=True),
        sa.Column("choices", JSONVariant, nullable=True),
        sa.Column("correct_keys", JSONVariant, nullable=False),
        sa.Column("multi_select", sa.Boolean(), nullable=False),
        sa.Column("dimension", sa.String(length=10), nullable=True),
        sa.Column("group_id", sa.Uuid(), nullable=True),
        sa.Column("explanation_md", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_quiz_questions_category_difficulty", "quiz_questions", ["category", "difficulty"], unique=False
    )
    op.create_index(op.f("ix_quiz_questions_group_id"), "quiz_questions", ["group_id"], unique=False)

    op.create_table(
        "quiz_sessions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("category", sa.String(length=20), nullable=False),
        sa.Column("duration_s", sa.Integer(), nullable=False),
        sa.Column("elapsed_s", sa.Float(), nullable=False),
        sa.Column("overall_score", sa.Float(), nullable=False),
        sa.Column("elo_delta", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_quiz_sessions_user_id"), "quiz_sessions", ["user_id"], unique=False)
    op.create_index(op.f("ix_quiz_sessions_created_at"), "quiz_sessions", ["created_at"], unique=False)

    op.create_table(
        "quiz_answers",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("session_id", sa.Uuid(), nullable=False),
        sa.Column("question_id", sa.Uuid(), nullable=False),
        sa.Column("selected_keys", JSONVariant, nullable=False),
        sa.Column("correct", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["session_id"], ["quiz_sessions.id"]),
        sa.ForeignKeyConstraint(["question_id"], ["quiz_questions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_quiz_answers_session_id"), "quiz_answers", ["session_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_quiz_answers_session_id"), table_name="quiz_answers")
    op.drop_table("quiz_answers")

    op.drop_index(op.f("ix_quiz_sessions_created_at"), table_name="quiz_sessions")
    op.drop_index(op.f("ix_quiz_sessions_user_id"), table_name="quiz_sessions")
    op.drop_table("quiz_sessions")

    op.drop_index(op.f("ix_quiz_questions_group_id"), table_name="quiz_questions")
    op.drop_index("ix_quiz_questions_category_difficulty", table_name="quiz_questions")
    op.drop_table("quiz_questions")

import uuid
from datetime import datetime, timezone

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Index, Integer, String, UniqueConstraint, Uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

JSONVariant = JSON().with_variant(JSONB, "postgresql")


def _uuid() -> uuid.UUID:
    return uuid.uuid4()


def _now() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=_uuid)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    ratings: Mapped[list["UserRating"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    elo_history: Mapped[list["EloHistory"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class UserRating(Base):
    """One row per (user, category). New categories are lazily created at 500 (Intern) on first session."""

    __tablename__ = "user_ratings"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=_uuid)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id"), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(20), nullable=False)
    rating: Mapped[int] = mapped_column(Integer, nullable=False, default=500)
    sessions_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    user: Mapped["User"] = relationship(back_populates="ratings")

    __table_args__ = (UniqueConstraint("user_id", "category", name="uq_user_ratings_user_id_category"),)


class EloHistory(Base):
    """Append-only log of every rating change, one row per scored session."""

    __tablename__ = "elo_history"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=_uuid)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id"), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(20), nullable=False)
    rating_before: Mapped[int] = mapped_column(Integer, nullable=False)
    rating_after: Mapped[int] = mapped_column(Integer, nullable=False)
    delta: Mapped[int] = mapped_column(Integer, nullable=False)
    source_type: Mapped[str] = mapped_column(String(20), nullable=False)
    source_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, index=True)

    user: Mapped["User"] = relationship(back_populates="elo_history")


class TypingSnippet(Base):
    """A piece of Python source used by both Typing Racer modes. Classic
    mode types the whole thing; Reaction mode splits `content` into lines."""

    __tablename__ = "typing_snippets"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=_uuid)
    language: Mapped[str] = mapped_column(String(20), nullable=False, default="python")
    difficulty: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(String, nullable=False)
    char_count: Mapped[int] = mapped_column(Integer, nullable=False)
    line_count: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class TypingAttempt(Base):
    """One completed Typing Racer session, either mode. Mode-specific columns
    are nullable; `input_log` holds the per-item submissions the score was
    computed from, for later review/debugging."""

    __tablename__ = "typing_attempts"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=_uuid)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id"), nullable=False, index=True)
    mode: Mapped[str] = mapped_column(String(20), nullable=False)
    duration_s: Mapped[int] = mapped_column(Integer, nullable=False)
    elapsed_s: Mapped[float] = mapped_column(Float, nullable=False)

    raw_wpm: Mapped[float | None] = mapped_column(Float, nullable=True)
    accuracy: Mapped[float | None] = mapped_column(Float, nullable=True)
    lines_correct: Mapped[int | None] = mapped_column(Integer, nullable=True)
    lines_total: Mapped[int | None] = mapped_column(Integer, nullable=True)

    score: Mapped[float] = mapped_column(Float, nullable=False)
    elo_delta: Mapped[int] = mapped_column(Integer, nullable=False)
    input_log: Mapped[list] = mapped_column(JSONVariant, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, index=True)


class ApproachPrompt(Base):
    """A quick-fire prompt ("explain your approach"). `grading_notes_md` is the
    intended optimal approach -- the judge grades against this ground truth
    rather than its own guess, and it's never sent to the client."""

    __tablename__ = "approach_prompts"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=_uuid)
    difficulty: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    prompt_md: Mapped[str] = mapped_column(String, nullable=False)
    grading_notes_md: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class ApproachSession(Base):
    """One completed 5-question quick-fire session, graded as a whole by Claude."""

    __tablename__ = "approach_sessions"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=_uuid)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id"), nullable=False, index=True)
    elapsed_s: Mapped[float] = mapped_column(Float, nullable=False)
    overall_score: Mapped[float] = mapped_column(Float, nullable=False)
    session_summary: Mapped[str] = mapped_column(String, nullable=False)
    elo_delta: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, index=True)


class ApproachAnswer(Base):
    """One graded answer within an approach session. `grade` holds Claude's
    structured per-dimension scores (0-100) + feedback for this answer."""

    __tablename__ = "approach_answers"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=_uuid)
    session_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("approach_sessions.id"), nullable=False, index=True)
    prompt_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("approach_prompts.id"), nullable=False)
    answer_text: Mapped[str] = mapped_column(String, nullable=False)
    grade: Mapped[dict] = mapped_column(JSONVariant, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class QuizQuestion(Base):
    """One multiple-choice / select-all-that-apply question, shared by all
    three quiz categories (python_trivia, systems_trivia, complexity) since
    they're mechanically identical and differ only in category/content-shape.

    For `category == "complexity"`: `code_snippet`/`language` hold the code to
    display, `choices` is left null (the frontend/router use the shared
    BIG_O_CHOICES constant instead of duplicating it on every row), and
    `dimension` ("time"/"space") plus `group_id` pair the two rows generated
    from one authored snippet so they render together as one screen."""

    __tablename__ = "quiz_questions"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=_uuid)
    category: Mapped[str] = mapped_column(String(20), nullable=False)
    topic: Mapped[str | None] = mapped_column(String(50), nullable=True)
    difficulty: Mapped[int] = mapped_column(Integer, nullable=False)
    prompt_md: Mapped[str] = mapped_column(String, nullable=False)
    code_snippet: Mapped[str | None] = mapped_column(String, nullable=True)
    language: Mapped[str | None] = mapped_column(String(20), nullable=True)
    choices: Mapped[list | None] = mapped_column(JSONVariant, nullable=True)
    correct_keys: Mapped[list] = mapped_column(JSONVariant, nullable=False)
    multi_select: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    dimension: Mapped[str | None] = mapped_column(String(10), nullable=True)
    group_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, nullable=True, index=True)
    explanation_md: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    __table_args__ = (
        # The adaptive-difficulty queue query filters by category and a
        # difficulty window -- unlike the other prompt tables (which just
        # load everything and random.choice/sample), this is a real access
        # pattern that needs an index or it becomes a full scan as the bank grows.
        Index("ix_quiz_questions_category_difficulty", "category", "difficulty"),
    )


class QuizSession(Base):
    """One timed quick-fire quiz round in any of the 3 quiz categories."""

    __tablename__ = "quiz_sessions"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=_uuid)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id"), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(20), nullable=False)
    duration_s: Mapped[int] = mapped_column(Integer, nullable=False)
    elapsed_s: Mapped[float] = mapped_column(Float, nullable=False)
    overall_score: Mapped[float] = mapped_column(Float, nullable=False)
    elo_delta: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, index=True)


class QuizAnswer(Base):
    """One submitted answer within a quiz session. Complexity screens write
    two independent rows per snippet (one per dimension) rather than a
    special-cased pair, so `overall_score` on the session is just the mean of
    `correct` across every answer row -- partial credit falls out for free."""

    __tablename__ = "quiz_answers"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=_uuid)
    session_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("quiz_sessions.id"), nullable=False, index=True)
    question_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("quiz_questions.id"), nullable=False)
    selected_keys: Mapped[list] = mapped_column(JSONVariant, nullable=False)
    correct: Mapped[bool] = mapped_column(Boolean, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

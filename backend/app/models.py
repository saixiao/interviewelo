import uuid
from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String, UniqueConstraint, Uuid
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


class DesignPrompt(Base):
    """A system-design interview prompt ("design a URL shortener") with concrete
    constraints baked into `prompt_md`. `rubric_md` is the ground-truth grading
    rubric describing what a strong answer covers -- the judge grades against it
    and it's never sent to the client, exactly like approach_prompts.grading_notes_md."""

    __tablename__ = "design_prompts"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=_uuid)
    difficulty: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    prompt_md: Mapped[str] = mapped_column(String, nullable=False)
    rubric_md: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class DesignSession(Base):
    """One timed system-design session. `transcript` is an append-only list of
    {role: "user"|"interviewer", text, ts} entries persisted incrementally so a
    long session survives a page refresh; `grade` holds Claude's structured
    debrief once the session is finished and graded."""

    __tablename__ = "design_sessions"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=_uuid)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id"), nullable=False, index=True)
    prompt_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("design_prompts.id"), nullable=False)
    duration_s: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="in_progress")
    transcript: Mapped[list] = mapped_column(JSONVariant, nullable=False, default=list)
    grade: Mapped[dict | None] = mapped_column(JSONVariant, nullable=True)
    overall_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    elo_delta: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, index=True)
    graded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

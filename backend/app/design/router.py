import random
from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.db import get_db
from app.design.schemas import (
    DesignFinishResponse,
    DesignGradeOut,
    DesignPromptOut,
    DesignSessionCreateRequest,
    DesignSessionCreateResponse,
    DesignSessionStateResponse,
    FollowUpResponse,
    MessageRequest,
    MessageResponse,
    RubricDimensionOut,
    TranscriptEntryOut,
)
from app.elo.engine import apply_session_result
from app.llm.grader import (
    DESIGN_RUBRIC_DIMENSIONS,
    generate_design_followup,
    grade_design_session,
)
from app.models import DesignPrompt, DesignSession, User

router = APIRouter(prefix="/design", tags=["design"])

MAX_FOLLOW_UPS = 5


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _get_owned_session(db: Session, session_id: UUID, user: User) -> DesignSession:
    session = (
        db.query(DesignSession)
        .filter(DesignSession.id == session_id, DesignSession.user_id == user.id)
        .one_or_none()
    )
    if session is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Session not found")
    return session


def _get_prompt(db: Session, session: DesignSession) -> DesignPrompt:
    prompt = db.query(DesignPrompt).filter(DesignPrompt.id == session.prompt_id).one_or_none()
    if prompt is None:  # pragma: no cover - prompts are never deleted while referenced
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Session prompt missing")
    return prompt


def _follow_ups_used(session: DesignSession) -> int:
    return sum(1 for entry in session.transcript if entry.get("role") == "interviewer")


def _remaining_s(session: DesignSession) -> int:
    created = session.created_at
    if created.tzinfo is None:  # SQLite returns naive datetimes in tests
        created = created.replace(tzinfo=timezone.utc)
    elapsed = (datetime.now(timezone.utc) - created).total_seconds()
    return max(0, round(session.duration_s - elapsed))


def _require_in_progress(session: DesignSession) -> None:
    if session.status != "in_progress":
        raise HTTPException(status.HTTP_409_CONFLICT, "Session is already graded")


@router.get("/rubric", response_model=list[RubricDimensionOut])
def get_rubric(_user: User = Depends(get_current_user)) -> list[RubricDimensionOut]:
    """The four 0-100 grading dimensions shown on session/results pages --
    kept in sync with the grading prompt via DESIGN_RUBRIC_DIMENSIONS."""
    return [RubricDimensionOut(**dim) for dim in DESIGN_RUBRIC_DIMENSIONS]


@router.post("/sessions", response_model=DesignSessionCreateResponse)
def create_session(
    body: DesignSessionCreateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> DesignSessionCreateResponse:
    prompts = db.query(DesignPrompt).all()
    if not prompts:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "No design prompts seeded yet")

    prompt = random.choice(prompts)
    session = DesignSession(
        user_id=user.id,
        prompt_id=prompt.id,
        duration_s=body.duration_s,
        status="in_progress",
        transcript=[],
    )
    db.add(session)
    db.commit()

    return DesignSessionCreateResponse(
        session_id=session.id,
        duration_s=session.duration_s,
        prompt=DesignPromptOut(title=prompt.title, prompt_md=prompt.prompt_md, difficulty=prompt.difficulty),
    )


@router.get("/sessions/{session_id}", response_model=DesignSessionStateResponse)
def get_session(
    session_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> DesignSessionStateResponse:
    """Resume endpoint: the transcript is persisted turn by turn, so a refresh
    mid-session re-fetches everything here and picks up where it left off."""
    session = _get_owned_session(db, session_id, user)
    prompt = _get_prompt(db, session)

    return DesignSessionStateResponse(
        session_id=session.id,
        status=session.status,
        duration_s=session.duration_s,
        remaining_s=_remaining_s(session),
        follow_ups_used=_follow_ups_used(session),
        transcript=[TranscriptEntryOut(**entry) for entry in session.transcript],
        prompt=DesignPromptOut(title=prompt.title, prompt_md=prompt.prompt_md, difficulty=prompt.difficulty),
    )


@router.post("/sessions/{session_id}/messages", response_model=MessageResponse)
def post_message(
    session_id: UUID,
    body: MessageRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> MessageResponse:
    session = _get_owned_session(db, session_id, user)
    _require_in_progress(session)

    text = body.text.strip()
    if not text:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Message text required")

    entry = {"role": "user", "text": text, "ts": _now_iso()}
    # Reassign (rather than mutate in place) so SQLAlchemy sees the JSON change.
    session.transcript = [*session.transcript, entry]
    db.commit()

    return MessageResponse(
        entry=TranscriptEntryOut(**entry),
        transcript=[TranscriptEntryOut(**e) for e in session.transcript],
    )


@router.post("/sessions/{session_id}/follow-up", response_model=FollowUpResponse)
def request_follow_up(
    session_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> FollowUpResponse:
    session = _get_owned_session(db, session_id, user)
    _require_in_progress(session)

    used = _follow_ups_used(session)
    if used >= MAX_FOLLOW_UPS:
        raise HTTPException(status.HTTP_409_CONFLICT, "Follow-up limit reached for this session")

    prompt = _get_prompt(db, session)

    try:
        question = generate_design_followup(prompt.title, prompt.prompt_md, session.transcript)
    except Exception as exc:
        raise HTTPException(
            status.HTTP_502_BAD_GATEWAY, "Could not generate a follow-up, please try again"
        ) from exc

    entry = {"role": "interviewer", "text": question, "ts": _now_iso()}
    session.transcript = [*session.transcript, entry]
    db.commit()

    return FollowUpResponse(
        entry=TranscriptEntryOut(**entry),
        follow_ups_used=used + 1,
        follow_ups_remaining=MAX_FOLLOW_UPS - (used + 1),
    )


@router.post("/sessions/{session_id}/finish", response_model=DesignFinishResponse)
def finish_session(
    session_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> DesignFinishResponse:
    session = _get_owned_session(db, session_id, user)
    _require_in_progress(session)

    prompt = _get_prompt(db, session)

    # An empty/near-empty transcript is still graded (very low score) rather
    # than erroring -- mirrors how the approach round handles blank answers.
    try:
        grade = grade_design_session(
            prompt.title, prompt.prompt_md, prompt.rubric_md, session.transcript
        )
    except Exception as exc:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, "Grading failed, please try again") from exc

    score = grade.overall / 100

    session.grade = grade.model_dump()
    session.overall_score = score
    session.status = "graded"
    session.graded_at = datetime.now(timezone.utc)

    session_result = apply_session_result(
        db,
        user.id,
        category="design",
        score=score,
        difficulty=prompt.difficulty,
        source_type="design_session",
        source_id=session.id,
    )
    session.elo_delta = session_result.delta
    db.commit()

    return DesignFinishResponse(
        grade=DesignGradeOut(**grade.model_dump()),
        overall_score=score,
        prompt_title=prompt.title,
        transcript=[TranscriptEntryOut(**e) for e in session.transcript],
        graded_at=session.graded_at,
        rating_before=session_result.rating_before,
        rating_after=session_result.rating_after,
        delta=session_result.delta,
        tier_before=session_result.tier_before,
        tier_after=session_result.tier_after,
    )

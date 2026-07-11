import json
import random
from typing import Iterator

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.approach.schemas import (
    AnswerGradeOut,
    ApproachAttemptRequest,
    ApproachAttemptResponse,
    ApproachQueueResponse,
    ChatRequest,
    ChatResponse,
    InfiniteAttemptRequest,
    QueuePromptOut,
    RubricDimensionOut,
)
from app.auth.dependencies import get_current_user
from app.db import SessionLocal, get_db
from app.elo.constants import STARTING_RATING
from app.elo.engine import SessionResult, apply_session_result, category_ratings, tier_for
from app.llm.grader import (
    RUBRIC_DIMENSIONS,
    GradingItem,
    chat_about_answer,
    grade_session,
    grade_single_stream,
    session_score,
)
from app.models import ApproachAnswer, ApproachPrompt, ApproachSession, User

router = APIRouter(prefix="/approach", tags=["approach"])

QUESTIONS_PER_SESSION = 5


@router.get("/rubric", response_model=list[RubricDimensionOut])
def get_rubric(_user: User = Depends(get_current_user)) -> list[RubricDimensionOut]:
    """The 0-100 scoring scale shown on session pages and the info page --
    kept in sync with the grading prompt via RUBRIC_DIMENSIONS."""
    return [RubricDimensionOut(**dim) for dim in RUBRIC_DIMENSIONS]


@router.get("/queue", response_model=ApproachQueueResponse)
def get_queue(
    count: int = Query(default=QUESTIONS_PER_SESSION, ge=1, le=20),
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
) -> ApproachQueueResponse:
    prompts = db.query(ApproachPrompt).all()
    if not prompts:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "No approach prompts seeded yet")

    chosen = random.sample(prompts, min(count, len(prompts)))
    return ApproachQueueResponse(
        items=[QueuePromptOut(prompt_id=p.id, title=p.title, prompt_md=p.prompt_md) for p in chosen]
    )


@router.post("/attempts", response_model=ApproachAttemptResponse)
def submit_attempt(
    body: ApproachAttemptRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ApproachAttemptResponse:
    if not body.items:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "items required")

    prompt_ids = {item.prompt_id for item in body.items}
    prompts = {
        p.id: p for p in db.query(ApproachPrompt).filter(ApproachPrompt.id.in_(prompt_ids)).all()
    }
    missing = prompt_ids - prompts.keys()
    if missing:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Unknown prompt id(s) submitted")

    grading_items = [
        GradingItem(
            title=prompts[item.prompt_id].title,
            prompt_md=prompts[item.prompt_id].prompt_md,
            grading_notes_md=prompts[item.prompt_id].grading_notes_md,
            answer_text=item.answer_text,
        )
        for item in body.items
    ]

    try:
        grade = grade_session(grading_items)
    except Exception as exc:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, "Grading failed, please try again") from exc

    score = session_score(grade)
    difficulty = round(
        sum(prompts[item.prompt_id].difficulty for item in body.items) / len(body.items)
    )

    session = ApproachSession(
        user_id=user.id,
        elapsed_s=body.elapsed_s,
        overall_score=score,
        session_summary=grade.session_summary,
        elo_delta=0,
    )
    db.add(session)
    db.flush()

    results: list[AnswerGradeOut] = []
    for item, answer_grade in zip(body.items, grade.answers):
        prompt = prompts[item.prompt_id]
        db.add(
            ApproachAnswer(
                session_id=session.id,
                prompt_id=prompt.id,
                answer_text=item.answer_text,
                grade=answer_grade.model_dump(),
            )
        )
        results.append(
            AnswerGradeOut(
                prompt_id=prompt.id,
                title=prompt.title,
                prompt_md=prompt.prompt_md,
                answer_text=item.answer_text,
                approach_correctness=answer_grade.approach_correctness,
                complexity_awareness=answer_grade.complexity_awareness,
                edge_case_awareness=answer_grade.edge_case_awareness,
                communication=answer_grade.communication,
                feedback=answer_grade.feedback,
            )
        )

    if body.is_infinite:
        # Infinite-mode attempts are unbounded practice, not a placement --
        # record the answer but leave the user's rating untouched.
        ratings = category_ratings(db, user.id)
        rating = ratings["approach"].rating if "approach" in ratings else STARTING_RATING
        tier = tier_for(rating)
        session_result = SessionResult(
            rating_before=rating, rating_after=rating, delta=0, tier_before=tier, tier_after=tier
        )
        session.elo_delta = 0
        db.commit()
    else:
        session_result = apply_session_result(
            db,
            user.id,
            category="approach",
            score=score,
            difficulty=difficulty,
            source_type="approach_session",
            source_id=session.id,
        )
        session.elo_delta = session_result.delta
        db.commit()

    return ApproachAttemptResponse(
        score=score,
        session_summary=grade.session_summary,
        results=results,
        rating_before=session_result.rating_before,
        rating_after=session_result.rating_after,
        delta=session_result.delta,
        tier_before=session_result.tier_before,
        tier_after=session_result.tier_after,
    )


def _sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


@router.post("/infinite/attempts")
def submit_infinite_attempt_stream(
    body: InfiniteAttemptRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> StreamingResponse:
    """SSE stream for infinite mode: emits Claude's live thinking while it
    grades a single answer, then a final `done` event with the grade. Elo is
    never touched here -- infinite mode is unbounded practice, not a placement.
    """
    prompt = db.query(ApproachPrompt).filter(ApproachPrompt.id == body.prompt_id).first()
    if prompt is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Unknown prompt id")

    prompt_id, title, prompt_md, grading_notes_md = (
        prompt.id,
        prompt.title,
        prompt.prompt_md,
        prompt.grading_notes_md,
    )
    item = GradingItem(
        title=title, prompt_md=prompt_md, grading_notes_md=grading_notes_md, answer_text=body.answer_text
    )
    user_id = user.id

    def event_stream() -> Iterator[str]:
        grade = None
        try:
            for event_type, payload in grade_single_stream(item):
                if event_type == "thinking":
                    yield _sse("thinking", {"text": payload})
                else:
                    grade = payload
        except Exception:
            yield _sse("error", {"message": "Could not grade that answer. Please try again."})
            return

        # A fresh session -- the request-scoped `db` dependency may already be
        # torn down by the time this generator body runs during response
        # streaming, so it can't be reused for the post-grade write.
        write_db = SessionLocal()
        try:
            session = ApproachSession(
                user_id=user_id,
                elapsed_s=body.elapsed_s,
                overall_score=0.0,
                session_summary="",
                elo_delta=0,
            )
            write_db.add(session)
            write_db.flush()
            write_db.add(
                ApproachAnswer(
                    session_id=session.id,
                    prompt_id=prompt_id,
                    answer_text=body.answer_text,
                    grade=grade.model_dump(),
                )
            )
            write_db.commit()
        finally:
            write_db.close()

        result = AnswerGradeOut(
            prompt_id=prompt_id,
            title=title,
            prompt_md=prompt_md,
            answer_text=body.answer_text,
            approach_correctness=grade.approach_correctness,
            complexity_awareness=grade.complexity_awareness,
            edge_case_awareness=grade.edge_case_awareness,
            communication=grade.communication,
            feedback=grade.feedback,
        )
        yield _sse("done", json.loads(result.model_dump_json()))

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@router.post("/chat", response_model=ChatResponse)
def chat_about_question(
    body: ChatRequest,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
) -> ChatResponse:
    """Post-grade follow-up chat: discuss the approach further after seeing the score."""
    prompt = db.query(ApproachPrompt).filter(ApproachPrompt.id == body.prompt_id).first()
    if prompt is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Unknown prompt id")

    item = GradingItem(
        title=prompt.title,
        prompt_md=prompt.prompt_md,
        grading_notes_md=prompt.grading_notes_md,
        answer_text=body.answer_text,
    )
    history = [{"role": m.role, "content": m.content} for m in body.messages]

    try:
        reply = chat_about_answer(item, body.feedback, history)
    except Exception as exc:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, "Chat failed, please try again") from exc

    return ChatResponse(reply=reply)

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.db import get_db
from app.elo.engine import apply_session_result
from app.models import QuizAnswer, QuizQuestion, QuizSession, User
from app.quiz.constants import BIG_O_CHOICES, QUIZ_CATEGORIES
from app.quiz.schemas import (
    AnswerResult,
    ChoiceOut,
    QueueQuestionOut,
    QuizAttemptRequest,
    QuizAttemptResponse,
    QuizQueueResponse,
    RevealRequest,
    RevealResponse,
)
from app.quiz.scoring import is_correct, mean_difficulty, overall_score
from app.quiz.selection import select_queue

router = APIRouter(prefix="/quiz", tags=["quiz"])

# Rough per-item pacing used to size how many questions to request for a
# given duration -- a code snippet takes longer to read than a trivia line.
SECONDS_PER_TRIVIA_ITEM = 20
SECONDS_PER_COMPLEXITY_ITEM = 40
QUEUE_OVERFETCH = 1.5
MIN_QUEUE_ITEMS = 8


def _validate_category(category: str) -> None:
    if category not in QUIZ_CATEGORIES:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Unknown quiz category")


def _target_count(category: str, duration_s: int) -> int:
    per_item = SECONDS_PER_COMPLEXITY_ITEM if category == "complexity" else SECONDS_PER_TRIVIA_ITEM
    estimate = max(1, duration_s // per_item)
    return max(MIN_QUEUE_ITEMS, round(estimate * QUEUE_OVERFETCH))


def _serialize_question(q: QuizQuestion) -> QueueQuestionOut:
    if q.category == "complexity":
        choices = [ChoiceOut(key=key, label=label) for key, label in BIG_O_CHOICES]
    else:
        choices = [ChoiceOut(**c) for c in (q.choices or [])]
    return QueueQuestionOut(
        id=q.id,
        category=q.category,
        topic=q.topic,
        difficulty=q.difficulty,
        prompt_md=q.prompt_md,
        code_snippet=q.code_snippet,
        language=q.language,
        choices=choices,
        multi_select=q.multi_select,
        dimension=q.dimension,
        group_id=q.group_id,
    )


@router.get("/{category}/queue", response_model=QuizQueueResponse)
def get_queue(
    category: str,
    duration_s: int = 180,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> QuizQueueResponse:
    _validate_category(category)
    target = _target_count(category, duration_s)
    questions = select_queue(db, user.id, category, target)
    if not questions:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "No quiz questions seeded yet")

    return QuizQueueResponse(
        category=category,
        duration_s=duration_s,
        questions=[_serialize_question(q) for q in questions],
    )


@router.post("/questions/{question_id}/reveal", response_model=RevealResponse)
def reveal_question(
    question_id: UUID,
    body: RevealRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),  # noqa: ARG001 -- auth-gated like every other quiz route
) -> RevealResponse:
    """Single-question, non-persisting reveal used by every quiz category's
    per-question "show correct answer" flow -- deliberately separate from
    /attempts so the session's official answer list (assembled client-side
    and submitted once at the end) is completely unaffected by this call."""
    q = db.query(QuizQuestion).filter(QuizQuestion.id == question_id).one_or_none()
    if q is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Unknown question id")

    return RevealResponse(
        correct=is_correct(body.selected_keys, q.correct_keys),
        correct_keys=q.correct_keys,
        explanation_md=q.explanation_md,
    )


@router.post("/{category}/attempts", response_model=QuizAttemptResponse)
def submit_attempt(
    category: str,
    body: QuizAttemptRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> QuizAttemptResponse:
    _validate_category(category)
    if not body.answers:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "No answers submitted")

    question_ids = {a.question_id for a in body.answers}
    questions = {q.id: q for q in db.query(QuizQuestion).filter(QuizQuestion.id.in_(question_ids)).all()}
    missing = question_ids - questions.keys()
    if missing:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Unknown question id(s) submitted")

    results: list[AnswerResult] = []
    correctness: list[bool] = []
    for answer in body.answers:
        q = questions[answer.question_id]
        correct = is_correct(answer.selected_keys, q.correct_keys)
        correctness.append(correct)
        results.append(
            AnswerResult(
                question_id=q.id,
                correct=correct,
                correct_keys=q.correct_keys,
                explanation_md=q.explanation_md,
                selected_keys=answer.selected_keys,
            )
        )

    score = overall_score(correctness)
    difficulty = mean_difficulty(list(questions.values()))

    session = QuizSession(
        user_id=user.id,
        category=category,
        duration_s=body.duration_s,
        elapsed_s=body.elapsed_s,
        overall_score=score,
        elo_delta=0,
    )
    db.add(session)
    db.flush()

    for answer, result in zip(body.answers, results):
        db.add(
            QuizAnswer(
                session_id=session.id,
                question_id=answer.question_id,
                selected_keys=answer.selected_keys,
                correct=result.correct,
            )
        )

    session_result = apply_session_result(
        db,
        user.id,
        category=category,
        score=score,
        difficulty=difficulty,
        source_type="quiz_session",
        source_id=session.id,
    )
    session.elo_delta = session_result.delta
    db.commit()

    return QuizAttemptResponse(
        category=category,
        overall_score=score,
        results=results,
        rating_before=session_result.rating_before,
        rating_after=session_result.rating_after,
        delta=session_result.delta,
        tier_before=session_result.tier_before,
        tier_after=session_result.tier_after,
    )

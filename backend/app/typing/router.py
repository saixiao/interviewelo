import random

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.db import get_db
from app.elo.constants import STARTING_RATING
from app.elo.engine import SessionResult, apply_session_result, category_ratings, tier_for
from app.models import TypingAttempt, TypingSnippet, User
from app.typing.ast_match import lines_match
from app.typing.schemas import (
    Mode,
    QueueItemOut,
    TypingAttemptRequest,
    TypingAttemptResponse,
    TypingQueueResponse,
)
from app.typing.scoring import ClassicItem, score_classic_attempt, score_reaction_attempt

router = APIRouter(prefix="/typing", tags=["typing"])

# However many items a shuffled queue is padded to, so a fast typist never
# runs out mid-session. Comfortably more than anyone clears in 5 minutes.
MIN_QUEUE_ITEMS = 60


def _non_blank_lines(content: str) -> list[tuple[int, str]]:
    return [(i, line) for i, line in enumerate(content.split("\n")) if line.strip()]


def _padded_shuffle(items: list[QueueItemOut]) -> list[QueueItemOut]:
    """Shuffle, then repeat shuffled copies until comfortably long so a fast
    session never runs out of items."""
    random.shuffle(items)
    result = list(items)
    while len(result) < MIN_QUEUE_ITEMS:
        extra = list(items)
        random.shuffle(extra)
        result.extend(extra)
    return result


@router.get("/queue", response_model=TypingQueueResponse)
def get_queue(
    mode: Mode,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
) -> TypingQueueResponse:
    snippets = db.query(TypingSnippet).all()
    if not snippets:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "No typing snippets seeded yet")

    if mode == "classic":
        items = [QueueItemOut(snippet_id=s.id, content=s.content) for s in snippets]
    else:
        items = [
            QueueItemOut(snippet_id=s.id, line_index=idx, content=line)
            for s in snippets
            for idx, line in _non_blank_lines(s.content)
        ]

    return TypingQueueResponse(mode=mode, items=_padded_shuffle(items))


def _fetch_snippets(db: Session, snippet_ids: set) -> dict:
    snippets = {s.id: s for s in db.query(TypingSnippet).filter(TypingSnippet.id.in_(snippet_ids)).all()}
    missing = snippet_ids - snippets.keys()
    if missing:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Unknown snippet id(s) submitted")
    return snippets


@router.post("/attempts", response_model=TypingAttemptResponse)
def submit_attempt(
    body: TypingAttemptRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> TypingAttemptResponse:
    if body.mode == "classic":
        if not body.classic_items:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "classic_items required for classic mode")

        snippets = _fetch_snippets(db, {item.snippet_id for item in body.classic_items})
        classic_pairs = [
            ClassicItem(target=snippets[item.snippet_id].content, typed=item.typed)
            for item in body.classic_items
        ]
        result = score_classic_attempt(classic_pairs, elapsed_s=body.elapsed_s)
        difficulty = round(
            sum(snippets[item.snippet_id].difficulty for item in body.classic_items)
            / len(body.classic_items)
        )

        attempt = TypingAttempt(
            user_id=user.id,
            mode="classic",
            duration_s=body.duration_s,
            elapsed_s=body.elapsed_s,
            raw_wpm=result.raw_wpm,
            accuracy=result.accuracy,
            score=result.score,
            elo_delta=0,
            input_log=[item.model_dump(mode="json") for item in body.classic_items],
        )
        response_fields = {
            "raw_wpm": result.raw_wpm,
            "net_wpm": result.net_wpm,
            "accuracy": result.accuracy,
        }

    else:
        if not body.reaction_items:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "reaction_items required for reaction mode")

        snippets = _fetch_snippets(db, {item.snippet_id for item in body.reaction_items})
        line_results = []
        for item in body.reaction_items:
            lines = snippets[item.snippet_id].content.split("\n")
            if not 0 <= item.line_index < len(lines):
                raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid line_index")
            line_results.append(lines_match(lines[item.line_index], item.typed))

        result = score_reaction_attempt(line_results, elapsed_s=body.elapsed_s)
        difficulty = round(
            sum(snippets[item.snippet_id].difficulty for item in body.reaction_items)
            / len(body.reaction_items)
        )

        attempt = TypingAttempt(
            user_id=user.id,
            mode="reaction",
            duration_s=body.duration_s,
            elapsed_s=body.elapsed_s,
            lines_correct=result.lines_correct,
            lines_total=result.lines_total,
            score=result.score,
            elo_delta=0,
            input_log=[
                {**item.model_dump(mode="json"), "correct": correct}
                for item, correct in zip(body.reaction_items, line_results)
            ],
        )
        response_fields = {"lines_correct": result.lines_correct, "lines_total": result.lines_total}

    db.add(attempt)
    db.flush()

    if body.duration_s == 0:
        # Infinite-mode sessions are unbounded practice, not a placement --
        # record the attempt but leave the user's rating untouched.
        ratings = category_ratings(db, user.id)
        rating = ratings["typing"].rating if "typing" in ratings else STARTING_RATING
        tier = tier_for(rating)
        session_result = SessionResult(
            rating_before=rating, rating_after=rating, delta=0, tier_before=tier, tier_after=tier
        )
        attempt.elo_delta = 0
        db.commit()
    else:
        session_result = apply_session_result(
            db,
            user.id,
            category="typing",
            score=result.score,
            difficulty=difficulty,
            source_type="typing_attempt",
            source_id=attempt.id,
        )
        attempt.elo_delta = session_result.delta
        db.commit()

    return TypingAttemptResponse(
        mode=body.mode,
        score=result.score,
        rating_before=session_result.rating_before,
        rating_after=session_result.rating_after,
        delta=session_result.delta,
        tier_before=session_result.tier_before,
        tier_after=session_result.tier_after,
        **response_fields,
    )

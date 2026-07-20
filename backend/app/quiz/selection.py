"""Adaptive-difficulty question selection for the quiz modes.

Unlike typing/approach (which pick content uniformly at random and let the
Elo *scoring* math be the only place rating matters), quiz
content *selection* itself adapts to the user's current rating: harder
questions get served as rating climbs. Kept separate from router.py so it's
unit-testable without a TestClient, mirroring elo/engine.py.
"""

import random
from uuid import UUID

from sqlalchemy.orm import Session

from app.elo.constants import STARTING_RATING
from app.elo.engine import category_ratings
from app.models import QuizAnswer, QuizQuestion, QuizSession

# Elo points either side of the user's current rating that the queue draws
# from; widened (not narrowed) when too few unseen questions fall inside it.
INITIAL_WINDOW = 150
WINDOW_GROWTH = 2.0
MAX_WIDENINGS = 2

# How many of the user's most recently answered questions in this category
# are excluded from selection. MCQ repeat-exposure is gameable in a way
# free-text/typing content isn't -- seeing the same question again lets you
# recall the letter, not re-derive the answer -- so (unlike typing, which
# pads its queue by repeating snippets) quiz queues must not repeat recently
# seen items.
RECENT_EXCLUDE_LIMIT = 100

_DIMENSION_ORDER = {"time": 0, "space": 1}


def _recently_answered_ids(db: Session, user_id: UUID, category: str) -> set[UUID]:
    rows = (
        db.query(QuizAnswer.question_id)
        .join(QuizSession, QuizAnswer.session_id == QuizSession.id)
        .filter(QuizSession.user_id == user_id, QuizSession.category == category)
        .order_by(QuizSession.created_at.desc())
        .limit(RECENT_EXCLUDE_LIMIT)
        .all()
    )
    return {row[0] for row in rows}


def select_queue(db: Session, user_id: UUID, category: str, target_count: int) -> list[QuizQuestion]:
    """Pick `target_count` items from a difficulty window centered on the
    user's current rating in `category`, widening the window (up to
    MAX_WIDENINGS times) if too few unseen questions fall inside it.
    Adapted once per session off rating_before -- no mid-session
    re-targeting (that would need a live single-answer-submit endpoint and
    materially more state than a quick-fire round needs).

    For "complexity", one queue item = one code snippet's {time, space}
    question pair (linked by `group_id`): `target_count` counts snippets, and
    the returned list has up to 2x that many QuizQuestion rows, time-row
    before space-row within each pair.

    May return fewer than `target_count` rows if the category's bank is
    thin even after widening -- callers should treat a short queue as normal
    (the client offers a "Finish now" button) rather than an error.
    """
    ratings = category_ratings(db, user_id)
    rating = ratings[category].rating if category in ratings else STARTING_RATING
    exclude_ids = _recently_answered_ids(db, user_id, category)

    query = db.query(QuizQuestion).filter(QuizQuestion.category == category)
    if category == "complexity":
        query = query.filter(QuizQuestion.dimension == "time")  # one row per snippet group

    window = float(INITIAL_WINDOW)
    candidates: list[QuizQuestion] = []
    for attempt in range(MAX_WIDENINGS + 1):
        windowed = query.filter(QuizQuestion.difficulty.between(rating - window, rating + window)).all()
        candidates = [q for q in windowed if q.id not in exclude_ids]
        if len(candidates) >= target_count or attempt == MAX_WIDENINGS:
            break
        window *= WINDOW_GROWTH

    chosen = random.sample(candidates, min(target_count, len(candidates)))
    random.shuffle(chosen)

    if category != "complexity":
        return chosen

    group_ids = [c.group_id for c in chosen]
    pair_rows = db.query(QuizQuestion).filter(QuizQuestion.group_id.in_(group_ids)).all()
    by_group: dict[UUID, list[QuizQuestion]] = {}
    for row in pair_rows:
        by_group.setdefault(row.group_id, []).append(row)

    result: list[QuizQuestion] = []
    for c in chosen:
        pair = sorted(by_group[c.group_id], key=lambda q: _DIMENSION_ORDER.get(q.dimension or "", 2))
        result.extend(pair)
    return result

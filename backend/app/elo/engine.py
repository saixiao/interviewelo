"""Pure-ish Elo rating engine shared by every practice mode.

Each mode normalizes its own session performance to a score S in [0, 1] and
picks a difficulty rating D for the content attempted, then calls
`apply_session_result`. Everything else (tiers, expected score, K-factor
schedule) lives here so it only needs to be tuned in one place.
"""

from dataclasses import dataclass
from uuid import UUID

from sqlalchemy.orm import Session

from app.elo.constants import (
    CATEGORIES,
    ELO_SPREAD,
    MAX_RATING,
    MIN_RATING,
    PLACEMENT_K,
    PLACEMENT_SESSIONS,
    STANDARD_K,
    STARTING_RATING,
    TIERS,
)
from app.models import EloHistory, UserRating


def tier_for(rating: int) -> str:
    """Name of the tier a rating falls into. TIERS is ascending, so the last
    entry whose lower bound is <= rating is the match."""
    rating = clamp(rating)
    tier_name = TIERS[0][0]
    for name, lower_bound in TIERS:
        if rating >= lower_bound:
            tier_name = name
        else:
            break
    return tier_name


def clamp(rating: int) -> int:
    return max(MIN_RATING, min(MAX_RATING, rating))


def expected_score(rating: int, difficulty: int) -> float:
    """Logistic expected outcome for a player at `rating` facing content at
    `difficulty`, mirroring the standard two-player Elo formula with the
    content's difficulty rating standing in for an opponent's rating."""
    return 1 / (1 + 10 ** ((difficulty - rating) / ELO_SPREAD))


def k_factor(sessions_count: int) -> int:
    return PLACEMENT_K if sessions_count < PLACEMENT_SESSIONS else STANDARD_K


@dataclass(frozen=True)
class SessionResult:
    rating_before: int
    rating_after: int
    delta: int
    tier_before: str
    tier_after: str


def apply_session_result(
    db: Session,
    user_id: UUID,
    category: str,
    score: float,
    difficulty: int,
    source_type: str,
    source_id: UUID | None = None,
) -> SessionResult:
    """Score a completed session: updates the user's rating for `category`
    and appends an `elo_history` row. `score` must already be normalized to
    [0, 1]; `difficulty` is the content's Elo-scale difficulty rating.

    Commits the transaction. Caller should not have other uncommitted writes
    on `db` it isn't prepared to have committed alongside this.
    """
    if not 0.0 <= score <= 1.0:
        raise ValueError(f"score must be in [0, 1], got {score}")

    user_rating = (
        db.query(UserRating)
        .filter(UserRating.user_id == user_id, UserRating.category == category)
        .with_for_update()
        .one_or_none()
    )
    if user_rating is None:
        user_rating = UserRating(
            user_id=user_id, category=category, rating=STARTING_RATING, sessions_count=0
        )
        db.add(user_rating)
        db.flush()

    rating_before = user_rating.rating
    expected = expected_score(rating_before, difficulty)
    k = k_factor(user_rating.sessions_count)
    delta = round(k * (score - expected))
    rating_after = clamp(rating_before + delta)

    user_rating.rating = rating_after
    user_rating.sessions_count += 1

    db.add(
        EloHistory(
            user_id=user_id,
            category=category,
            rating_before=rating_before,
            rating_after=rating_after,
            delta=rating_after - rating_before,
            source_type=source_type,
            source_id=source_id,
        )
    )
    db.commit()

    return SessionResult(
        rating_before=rating_before,
        rating_after=rating_after,
        delta=rating_after - rating_before,
        tier_before=tier_for(rating_before),
        tier_after=tier_for(rating_after),
    )


def category_ratings(db: Session, user_id: UUID) -> dict[str, UserRating]:
    """All rating rows for a user, keyed by category. Categories with no
    sessions yet simply won't have a key here; callers should treat a
    missing category as the starting rating."""
    rows = db.query(UserRating).filter(UserRating.user_id == user_id).all()
    return {row.category: row for row in rows}


def overall_rating(db: Session, user_id: UUID) -> int:
    """Mean of the category ratings. Unplayed categories count at the
    starting rating so the overall number is meaningful from day one and
    playing every mode is what raises it."""
    ratings = category_ratings(db, user_id)
    values = [ratings[cat].rating if cat in ratings else STARTING_RATING for cat in CATEGORIES]
    return round(sum(values) / len(values))

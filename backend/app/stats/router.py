from datetime import date, datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.elo.constants import CATEGORIES, STARTING_RATING
from app.elo.engine import category_ratings, overall_rating, tier_bounds, tier_for
from app.db import get_db
from app.models import EloHistory, User
from app.stats.schemas import CategorySummary, EloHistoryPoint, EloHistoryResponse, StatsSummaryResponse

router = APIRouter(prefix="/stats", tags=["stats"])


def _as_utc_date(value: datetime) -> date:
    if value.tzinfo is None:  # SQLite returns naive datetimes in tests
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).date()


def _compute_streak(active_dates: set[date], today: date) -> int:
    """Consecutive days with at least one scored session, ending today or
    (if nothing happened yet today) yesterday -- so the streak doesn't reset
    to zero the moment the clock rolls over before the user has practiced."""
    if today in active_dates:
        cursor = today
    elif today - timedelta(days=1) in active_dates:
        cursor = today - timedelta(days=1)
    else:
        return 0

    streak = 0
    while cursor in active_dates:
        streak += 1
        cursor -= timedelta(days=1)
    return streak


@router.get("/elo-history", response_model=EloHistoryResponse)
def elo_history(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> EloHistoryResponse:
    rows = (
        db.query(EloHistory)
        .filter(EloHistory.user_id == user.id)
        .order_by(EloHistory.created_at.asc())
        .all()
    )
    return EloHistoryResponse(
        history=[
            EloHistoryPoint(
                category=row.category,
                rating_before=row.rating_before,
                rating_after=row.rating_after,
                delta=row.delta,
                source_type=row.source_type,
                created_at=row.created_at,
            )
            for row in rows
        ]
    )


@router.get("/summary", response_model=StatsSummaryResponse)
def summary(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> StatsSummaryResponse:
    """Dashboard hero data: overall Elo + tier progress, streak, and
    per-category peak rating / sessions played today -- all derived from
    `elo_history` so it stays accurate even if a mode's own scoring changes."""
    rows = db.query(EloHistory).filter(EloHistory.user_id == user.id).all()

    today = datetime.now(timezone.utc).date()
    best_rating: dict[str, int] = {}
    sessions_today: dict[str, int] = {}
    active_dates: set[date] = set()

    for row in rows:
        row_date = _as_utc_date(row.created_at)
        active_dates.add(row_date)
        best_rating[row.category] = max(best_rating.get(row.category, row.rating_after), row.rating_after)
        if row_date == today:
            sessions_today[row.category] = sessions_today.get(row.category, 0) + 1

    ratings = category_ratings(db, user.id)
    categories = [
        CategorySummary(
            category=cat,
            rating=ratings[cat].rating if cat in ratings else STARTING_RATING,
            tier=tier_for(ratings[cat].rating if cat in ratings else STARTING_RATING),
            sessions_count=ratings[cat].sessions_count if cat in ratings else 0,
            best_rating=best_rating.get(cat, STARTING_RATING),
            sessions_today=sessions_today.get(cat, 0),
        )
        for cat in CATEGORIES
    ]

    overall = overall_rating(db, user.id)
    floor, next_floor = tier_bounds(overall)
    return StatsSummaryResponse(
        overall_rating=overall,
        overall_tier=tier_for(overall),
        tier_floor=floor,
        tier_next_floor=next_floor,
        streak_days=_compute_streak(active_dates, today),
        categories=categories,
    )

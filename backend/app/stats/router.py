from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.db import get_db
from app.models import EloHistory, User
from app.stats.schemas import EloHistoryPoint, EloHistoryResponse

router = APIRouter(prefix="/stats", tags=["stats"])


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

from datetime import datetime

from pydantic import BaseModel


class EloHistoryPoint(BaseModel):
    category: str
    rating_before: int
    rating_after: int
    delta: int
    source_type: str
    created_at: datetime


class EloHistoryResponse(BaseModel):
    history: list[EloHistoryPoint]


class CategorySummary(BaseModel):
    category: str
    rating: int
    tier: str
    sessions_count: int
    best_rating: int
    sessions_today: int


class StatsSummaryResponse(BaseModel):
    overall_rating: int
    overall_tier: str
    tier_floor: int
    tier_next_floor: int | None
    streak_days: int
    categories: list[CategorySummary]

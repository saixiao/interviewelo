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

from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

Mode = Literal["classic", "reaction"]
# 0 is the "infinite" sentinel: no fixed duration, the user ends the session manually.
DurationS = Literal[60, 300, 0]


class QueueItemOut(BaseModel):
    snippet_id: UUID
    line_index: int | None = None  # None for classic (whole snippet typed)
    content: str


class TypingQueueResponse(BaseModel):
    mode: Mode
    items: list[QueueItemOut]


class ClassicSubmissionItem(BaseModel):
    snippet_id: UUID
    typed: str


class ReactionSubmissionItem(BaseModel):
    snippet_id: UUID
    line_index: int
    typed: str


class TypingAttemptRequest(BaseModel):
    mode: Mode
    duration_s: DurationS
    elapsed_s: float = Field(gt=0)
    classic_items: list[ClassicSubmissionItem] | None = None
    reaction_items: list[ReactionSubmissionItem] | None = None


class TypingAttemptResponse(BaseModel):
    mode: Mode
    score: float
    rating_before: int
    rating_after: int
    delta: int
    tier_before: str
    tier_after: str
    raw_wpm: float | None = None
    net_wpm: float | None = None
    accuracy: float | None = None
    lines_correct: int | None = None
    lines_total: int | None = None

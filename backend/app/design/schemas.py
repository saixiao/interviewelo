from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class DesignSessionCreateRequest(BaseModel):
    # 20 / 30 / 40 minutes in the UI; the server just bounds it sanely.
    duration_s: int = Field(ge=60, le=7200)


class DesignPromptOut(BaseModel):
    title: str
    prompt_md: str
    difficulty: int


class TranscriptEntryOut(BaseModel):
    role: str
    text: str
    ts: str


class DesignSessionCreateResponse(BaseModel):
    session_id: UUID
    duration_s: int
    prompt: DesignPromptOut


class DesignSessionStateResponse(BaseModel):
    """Everything the client needs to resume an in-progress session after a
    refresh -- never includes rubric_md."""

    session_id: UUID
    status: str
    duration_s: int
    remaining_s: int
    follow_ups_used: int
    transcript: list[TranscriptEntryOut]
    prompt: DesignPromptOut


class MessageRequest(BaseModel):
    text: str


class MessageResponse(BaseModel):
    entry: TranscriptEntryOut
    transcript: list[TranscriptEntryOut]


class FollowUpResponse(BaseModel):
    entry: TranscriptEntryOut
    follow_ups_used: int
    follow_ups_remaining: int


class DesignGradeOut(BaseModel):
    requirements: int
    high_level_design: int
    deep_dives: int
    tradeoffs_and_scaling: int
    strengths: list[str]
    improvements: list[str]
    overall: int


class DesignFinishResponse(BaseModel):
    grade: DesignGradeOut
    overall_score: float
    prompt_title: str
    transcript: list[TranscriptEntryOut]
    graded_at: datetime
    rating_before: int
    rating_after: int
    delta: int
    tier_before: str
    tier_after: str


class RubricDimensionOut(BaseModel):
    key: str
    label: str
    description: str

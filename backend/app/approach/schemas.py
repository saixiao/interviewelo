from uuid import UUID

from pydantic import BaseModel, Field


class QueuePromptOut(BaseModel):
    prompt_id: UUID
    title: str
    prompt_md: str


class ApproachQueueResponse(BaseModel):
    items: list[QueuePromptOut]


class AnswerSubmission(BaseModel):
    prompt_id: UUID
    answer_text: str


class ApproachAttemptRequest(BaseModel):
    elapsed_s: float = Field(gt=0)
    items: list[AnswerSubmission]
    # Infinite-mode attempts grade a single question at a time and never touch
    # Elo -- same "unbounded practice, not a placement" semantics as typing's
    # infinite mode.
    is_infinite: bool = False


class AnswerGradeOut(BaseModel):
    prompt_id: UUID
    title: str
    prompt_md: str
    answer_text: str
    approach_correctness: int
    complexity_awareness: int
    edge_case_awareness: int
    communication: int
    feedback: str


class ApproachAttemptResponse(BaseModel):
    score: float
    session_summary: str
    results: list[AnswerGradeOut]
    rating_before: int
    rating_after: int
    delta: int
    tier_before: str
    tier_after: str


class RubricDimensionOut(BaseModel):
    key: str
    label: str
    description: str


class InfiniteAttemptRequest(BaseModel):
    prompt_id: UUID
    answer_text: str
    elapsed_s: float = Field(gt=0)


class ChatMessageIn(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    # Only prompt_id is trusted for looking up ground-truth grading notes --
    # title/prompt_md/grading_notes_md are re-fetched server-side rather than
    # trusting client-supplied copies.
    prompt_id: UUID
    answer_text: str
    feedback: str
    messages: list[ChatMessageIn]


class ChatResponse(BaseModel):
    reply: str

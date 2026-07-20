from uuid import UUID

from pydantic import BaseModel, Field


class ChoiceOut(BaseModel):
    key: str
    label: str


class QueueQuestionOut(BaseModel):
    id: UUID
    category: str
    topic: str | None = None
    difficulty: int
    prompt_md: str
    code_snippet: str | None = None
    language: str | None = None
    choices: list[ChoiceOut]
    multi_select: bool
    dimension: str | None = None
    group_id: UUID | None = None


class QuizQueueResponse(BaseModel):
    category: str
    duration_s: int
    questions: list[QueueQuestionOut]


class AnswerSubmission(BaseModel):
    question_id: UUID
    selected_keys: list[str]


class QuizAttemptRequest(BaseModel):
    duration_s: int
    elapsed_s: float = Field(gt=0)
    answers: list[AnswerSubmission]


class AnswerResult(BaseModel):
    question_id: UUID
    correct: bool
    correct_keys: list[str]
    explanation_md: str
    selected_keys: list[str]


class QuizAttemptResponse(BaseModel):
    category: str
    overall_score: float
    results: list[AnswerResult]
    rating_before: int
    rating_after: int
    delta: int
    tier_before: str
    tier_after: str


class RevealRequest(BaseModel):
    selected_keys: list[str]


class RevealResponse(BaseModel):
    correct: bool
    correct_keys: list[str]
    explanation_md: str

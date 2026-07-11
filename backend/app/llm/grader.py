"""Anthropic client wrapper + structured-output grader for the quick-fire
approach round. This is the single place later LLM-judged modes (e.g. system
design) reuse for their own Claude grading calls.
"""

from dataclasses import dataclass
from typing import Iterator, Literal

import anthropic
from pydantic import BaseModel, Field

from app.config import get_settings

# Static across every grading call -- gets cache_control so repeated grading
# calls only pay full price for the varying per-session content appended after it.
GRADING_RUBRIC = """You are grading a candidate's answers in a quick-fire technical interview \
practice round. For each question, the candidate read a short problem statement and wrote a \
plain-English description of their approach -- no code, just the strategy they'd use to solve it.

Grade each answer against the provided ground-truth approach notes, not against your own \
independent solution -- the notes describe the intended optimal approach for that specific \
question, and answers should be judged relative to it.

Score each answer on four independent 0-100 dimensions:
- approach_correctness: Does the described approach actually solve the problem correctly and \
efficiently, per the ground truth? A correct approach described informally should score highly \
even if the wording is imprecise; a fundamentally wrong or missing approach should score low.
- complexity_awareness: Does the candidate demonstrate awareness of the time/space complexity of \
their approach, whether explicitly stated or implied by their description?
- edge_case_awareness: Does the candidate mention or account for edge cases relevant to this \
problem (empty input, duplicates, overflow, negative values, etc., as applicable)?
- communication: Is the explanation clear, well-organized, and understandable, independent of \
whether the underlying approach is correct?

Also write a 1-2 sentence `feedback` string for each answer: specific, actionable, and honest -- \
name what was right or wrong, don't just restate the score.

Finally write a `session_summary`: 2-3 sentences on the candidate's overall performance across \
all questions, noting any pattern (e.g. consistently strong on complexity, weak on edge cases).

Return exactly one graded answer per question, in the same order the questions are presented."""

# Mirrors the four dimensions described in GRADING_RUBRIC above -- the single
# source of truth for what the 0-100 scale on each dimension means, surfaced
# to the frontend via GET /approach/rubric so the scoring scale is never a
# black box.
RUBRIC_DIMENSIONS: list[dict[str, str]] = [
    {
        "key": "approach_correctness",
        "label": "Approach correctness",
        "description": (
            "Does the described approach actually solve the problem correctly and efficiently? "
            "A correct approach described informally still scores highly; a wrong or missing "
            "approach scores low."
        ),
    },
    {
        "key": "complexity_awareness",
        "label": "Complexity awareness",
        "description": (
            "Does the candidate show awareness of the time/space complexity of their approach, "
            "whether stated explicitly or implied by the description?"
        ),
    },
    {
        "key": "edge_case_awareness",
        "label": "Edge case awareness",
        "description": (
            "Does the candidate mention or account for edge cases relevant to the problem -- "
            "empty input, duplicates, overflow, negative values, etc.?"
        ),
    },
    {
        "key": "communication",
        "label": "Communication",
        "description": (
            "Is the explanation clear, well-organized, and understandable -- independent of "
            "whether the underlying approach is correct?"
        ),
    },
]

DESIGN_CHAT_SYSTEM = """You are a friendly, sharp technical interview coach. The candidate just \
answered a quick-fire approach-round question and received a grade from you. Now they want to \
keep discussing it -- clarifying questions, alternative approaches, complexity tradeoffs, edge \
cases, or anything else about the problem.

Be conversational and concise (a few sentences per reply, not an essay). Prefer a Socratic style \
-- ask a guiding question or nudge them toward the insight -- over immediately dumping the full \
ground-truth solution, unless they explicitly ask for it or are clearly stuck. You have the \
ground-truth approach notes for this question; use them to correct misconceptions and keep the \
discussion accurate."""


class AnswerGrade(BaseModel):
    approach_correctness: int = Field(ge=0, le=100)
    complexity_awareness: int = Field(ge=0, le=100)
    edge_case_awareness: int = Field(ge=0, le=100)
    communication: int = Field(ge=0, le=100)
    feedback: str


class SessionGrade(BaseModel):
    answers: list[AnswerGrade]
    session_summary: str


@dataclass(frozen=True)
class GradingItem:
    title: str
    prompt_md: str
    grading_notes_md: str
    answer_text: str


_client: anthropic.Anthropic | None = None


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=get_settings().anthropic_api_key)
    return _client


def _build_user_content(items: list[GradingItem]) -> str:
    blocks = [
        f"### Question {i}: {item.title}\n\n"
        f"**Prompt:**\n{item.prompt_md}\n\n"
        f"**Ground-truth approach notes (grade against this):**\n{item.grading_notes_md}\n\n"
        f"**Candidate's answer:**\n{item.answer_text or '(no answer submitted)'}"
        for i, item in enumerate(items, start=1)
    ]
    return "\n\n---\n\n".join(blocks)


def grade_session(items: list[GradingItem]) -> SessionGrade:
    """One messages.parse() call grading the whole session at once."""
    client = _get_client()
    response = client.messages.parse(
        model=get_settings().grading_model,
        max_tokens=4096,
        thinking={"type": "adaptive"},
        output_config={"effort": "low"},
        system=[{"type": "text", "text": GRADING_RUBRIC, "cache_control": {"type": "ephemeral"}}],
        messages=[{"role": "user", "content": _build_user_content(items)}],
        output_format=SessionGrade,
    )
    grade = response.parsed_output
    if grade is None or len(grade.answers) != len(items):
        raise ValueError("Grading response did not match the number of submitted answers")
    return grade


StreamEvent = tuple[Literal["thinking", "done"], str | AnswerGrade]


def grade_single_stream(item: GradingItem) -> Iterator[StreamEvent]:
    """Streams Claude's thinking while grading a single infinite-mode answer,
    then yields a final ("done", AnswerGrade) event once the graded output parses.
    """
    client = _get_client()
    with client.messages.stream(
        model=get_settings().grading_model,
        # Generous headroom over the ~200-300 tokens a single grade needs --
        # adaptive thinking occasionally kicks in even at low effort, and a
        # tight budget can truncate the JSON output after thinking eats it.
        max_tokens=4096,
        thinking={"type": "adaptive", "display": "summarized"},
        output_config={"effort": "low"},
        system=[{"type": "text", "text": GRADING_RUBRIC, "cache_control": {"type": "ephemeral"}}],
        messages=[{"role": "user", "content": _build_user_content([item])}],
        # Use the same SessionGrade schema grade_session() uses (a list of
        # answers + session_summary) even though this call only ever grades
        # one item. GRADING_RUBRIC's instructions talk about grading a whole
        # session and writing a session_summary; pairing it with a schema
        # that has neither confuses the model into leaking self-correction
        # text into the feedback field instead of a clean answer.
        output_format=SessionGrade,
    ) as stream:
        for event in stream:
            if event.type == "content_block_delta" and event.delta.type == "thinking_delta":
                yield ("thinking", event.delta.thinking)
        final = stream.get_final_message()

    session_grade = final.parsed_output
    if session_grade is None or len(session_grade.answers) != 1:
        raise ValueError("Grading response did not parse")
    grade = session_grade.answers[0]
    yield ("done", grade)


def chat_about_answer(item: GradingItem, feedback: str, history: list[dict[str, str]]) -> str:
    """One-off follow-up reply in the post-grade discussion chat for a single question."""
    client = _get_client()
    context = (
        f"### Question: {item.title}\n\n{item.prompt_md}\n\n"
        f"**Ground-truth approach notes:**\n{item.grading_notes_md}\n\n"
        f"**Candidate's answer:**\n{item.answer_text or '(no answer submitted)'}\n\n"
        f"**Feedback you gave:**\n{feedback}"
    )
    messages = [
        {"role": "user", "content": context},
        {"role": "assistant", "content": "Got it -- I've got your answer and my feedback in front of me. What would you like to dig into?"},
        *history,
    ]
    response = client.messages.create(
        model=get_settings().grading_model,
        max_tokens=1024,
        thinking={"type": "adaptive"},
        output_config={"effort": "low"},
        system=[{"type": "text", "text": DESIGN_CHAT_SYSTEM, "cache_control": {"type": "ephemeral"}}],
        messages=messages,
    )
    return next(b.text for b in response.content if b.type == "text")


# --- System design round -------------------------------------------------
#
# Static across every design-round call, so both prompts get cache_control:
# the varying per-session content (prompt + transcript) is appended after them.

DESIGN_FOLLOWUP_SYSTEM = """You are an experienced system-design interviewer running a timed mock \
interview. The candidate was given a design prompt with concrete constraints and is writing their \
design; the transcript so far (their writing plus any earlier questions you asked) is provided.

Ask exactly ONE incisive follow-up question that probes a real gap in their design so far: a \
component they glossed over, a tradeoff they made but didn't justify, a stated constraint their \
design doesn't clearly meet, a failure mode or bottleneck they haven't considered, or a data-model \
detail left vague. Prefer the most consequential gap over a nitpick, and don't repeat the substance \
of a question you already asked earlier in the transcript.

If the candidate has written little or nothing yet, ask an opening probing question about how their \
design will handle the most demanding constraint in the prompt.

Reply with the question only: no preamble, no evaluation of their work so far, no answering it \
yourself. At most two sentences."""

DESIGN_GRADING_SYSTEM = """You are grading a timed mock system-design interview. The candidate was \
given a design prompt with concrete numeric constraints and wrote their design in prose; an \
interviewer occasionally asked probing follow-up questions which the candidate answered inline. \
The full transcript is provided, along with a ground-truth rubric describing what a strong answer \
to this specific prompt covers.

Grade the transcript against the provided rubric, not against your own independent ideal design -- \
the rubric is the source of truth for what mattered for this prompt. Score four independent 0-100 \
dimensions:
- requirements: Did the candidate identify the functional and non-functional requirements that \
matter -- scale numbers, latency targets, consistency/availability needs -- and let them drive the \
design, rather than designing in a vacuum?
- high_level_design: Are the core components and their interactions right? Clear request flow, \
sensible API surface, a workable data model, appropriate storage choices.
- deep_dives: Did the candidate go deep on the 1-2 areas the rubric flags as critical for this \
system, with concrete mechanisms rather than hand-waving?
- tradeoffs_and_scaling: Did the candidate justify choices against alternatives, address \
bottlenecks and failure modes, and explain how the design meets the stated scale and latency \
constraints?

Then write the debrief -- this is what the candidate learns from, so make it count:
- strengths: 2-5 short bullet strings naming what the design genuinely got right. Be specific \
("chose fan-out-on-write and correctly excluded celebrity accounts"), not generic praise.
- improvements: 3-7 short bullet strings -- the things the design MISSED. Concrete gaps, gotchas, \
and unaddressed rubric points a strong answer would have covered ("never addressed how short-code \
collisions are handled", "no story for the 50ms p99 redirect target -- needed a cache in front of \
the store"). Order them most important first. This is the most valuable part of the debrief.
- overall: a holistic 0-100 score for the session.

If the transcript is empty or nearly empty, score all dimensions very low (0-10), say so plainly, \
and use `improvements` to list the most important things a design for this prompt needed to cover."""

# Mirrors the four dimensions in DESIGN_GRADING_SYSTEM -- surfaced to the
# frontend via GET /design/rubric so the scoring scale is never a black box.
DESIGN_RUBRIC_DIMENSIONS: list[dict[str, str]] = [
    {
        "key": "requirements",
        "label": "Requirements",
        "description": (
            "Did the answer pin down the functional and non-functional requirements that matter -- "
            "scale, latency, consistency -- and let them drive the design?"
        ),
    },
    {
        "key": "high_level_design",
        "label": "High-level design",
        "description": (
            "Are the core components, request flow, API surface, data model, and storage choices "
            "right for this system?"
        ),
    },
    {
        "key": "deep_dives",
        "label": "Deep dives",
        "description": (
            "Did the answer go deep on the 1-2 areas that are critical for this specific system, "
            "with concrete mechanisms rather than hand-waving?"
        ),
    },
    {
        "key": "tradeoffs_and_scaling",
        "label": "Tradeoffs & scaling",
        "description": (
            "Were choices justified against alternatives, and were bottlenecks, failure modes, and "
            "the stated scale/latency constraints addressed?"
        ),
    },
]


class DesignGrade(BaseModel):
    requirements: int = Field(ge=0, le=100)
    high_level_design: int = Field(ge=0, le=100)
    deep_dives: int = Field(ge=0, le=100)
    tradeoffs_and_scaling: int = Field(ge=0, le=100)
    strengths: list[str]
    improvements: list[str]
    overall: int = Field(ge=0, le=100)


def _render_transcript(transcript: list[dict]) -> str:
    if not transcript:
        return "(the candidate did not write anything)"
    blocks = []
    for entry in transcript:
        speaker = "Interviewer" if entry.get("role") == "interviewer" else "Candidate"
        blocks.append(f"**{speaker}:**\n{entry.get('text', '')}")
    return "\n\n".join(blocks)


def generate_design_followup(title: str, prompt_md: str, transcript: list[dict]) -> str:
    """One probing interviewer question based on the design prompt + transcript so far.
    Runs at low effort -- question generation doesn't need deep thinking and the
    user is mid-session waiting on it."""
    client = _get_client()
    content = (
        f"### Design prompt: {title}\n\n{prompt_md}\n\n"
        f"### Transcript so far\n\n{_render_transcript(transcript)}"
    )
    response = client.messages.create(
        model=get_settings().grading_model,
        max_tokens=1024,
        thinking={"type": "adaptive"},
        output_config={"effort": "low"},
        system=[{"type": "text", "text": DESIGN_FOLLOWUP_SYSTEM, "cache_control": {"type": "ephemeral"}}],
        messages=[{"role": "user", "content": content}],
    )
    return next(b.text for b in response.content if b.type == "text").strip()


def grade_design_session(
    title: str, prompt_md: str, rubric_md: str, transcript: list[dict]
) -> DesignGrade:
    """One messages.parse() call grading the full design transcript against the
    prompt's ground-truth rubric. Adaptive thinking at default effort -- this is
    a one-shot call whose quality is the whole debrief, so it's worth the latency."""
    client = _get_client()
    content = (
        f"### Design prompt: {title}\n\n{prompt_md}\n\n"
        f"### Ground-truth rubric (grade against this)\n\n{rubric_md}\n\n"
        f"### Interview transcript\n\n{_render_transcript(transcript)}"
    )
    response = client.messages.parse(
        model=get_settings().grading_model,
        max_tokens=8192,
        thinking={"type": "adaptive"},
        system=[{"type": "text", "text": DESIGN_GRADING_SYSTEM, "cache_control": {"type": "ephemeral"}}],
        messages=[{"role": "user", "content": content}],
        output_format=DesignGrade,
    )
    grade = response.parsed_output
    if grade is None:
        raise ValueError("Design grading response did not parse")
    return grade


def session_score(grade: SessionGrade) -> float:
    """S in [0, 1]: mean of all per-dimension scores across every answer."""
    dims = [
        value
        for answer in grade.answers
        for value in (
            answer.approach_correctness,
            answer.complexity_awareness,
            answer.edge_case_awareness,
            answer.communication,
        )
    ]
    return (sum(dims) / len(dims)) / 100 if dims else 0.0

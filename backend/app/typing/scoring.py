"""Pure scoring functions for both Typing Racer modes. Callers resolve
snippet/line content server-side before calling these -- never trust a
client-supplied "target" string, or accuracy becomes trivially gameable.
"""

from dataclasses import dataclass
from typing import NamedTuple

from app.typing.constants import (
    CLASSIC_NET_WPM_CEILING,
    CLASSIC_NET_WPM_FLOOR,
    REACTION_ACCURACY_WEIGHT,
    REACTION_LPM_CEILING,
    REACTION_LPM_FLOOR,
    REACTION_SPEED_WEIGHT,
)


def _piecewise_linear(value: float, floor: float, ceiling: float) -> float:
    if value <= floor:
        return 0.0
    if value >= ceiling:
        return 1.0
    return (value - floor) / (ceiling - floor)


class ClassicItem(NamedTuple):
    target: str
    typed: str


@dataclass(frozen=True)
class ClassicResult:
    raw_wpm: float
    accuracy: float
    net_wpm: float
    score: float


def score_classic_attempt(items: list[ClassicItem], elapsed_s: float) -> ClassicResult:
    if elapsed_s <= 0:
        raise ValueError("elapsed_s must be positive")
    if not items:
        return ClassicResult(raw_wpm=0.0, accuracy=1.0, net_wpm=0.0, score=0.0)

    correct_chars = 0
    total_chars = 0
    typed_chars = 0
    for target, typed in items:
        overlap = min(len(target), len(typed))
        correct_chars += sum(1 for i in range(overlap) if target[i] == typed[i])
        total_chars += max(len(target), len(typed))
        typed_chars += len(typed)

    minutes = elapsed_s / 60
    accuracy = correct_chars / total_chars if total_chars else 1.0
    raw_wpm = (typed_chars / 5) / minutes
    net_wpm = raw_wpm * accuracy**2
    score = _piecewise_linear(net_wpm, CLASSIC_NET_WPM_FLOOR, CLASSIC_NET_WPM_CEILING)

    return ClassicResult(raw_wpm=raw_wpm, accuracy=accuracy, net_wpm=net_wpm, score=score)


@dataclass(frozen=True)
class ReactionResult:
    lines_correct: int
    lines_total: int
    correct_ratio: float
    lines_per_minute: float
    speed_score: float
    score: float


def score_reaction_attempt(line_results: list[bool], elapsed_s: float) -> ReactionResult:
    if elapsed_s <= 0:
        raise ValueError("elapsed_s must be positive")

    lines_total = len(line_results)
    lines_correct = sum(line_results)
    minutes = elapsed_s / 60

    correct_ratio = lines_correct / lines_total if lines_total else 0.0
    lines_per_minute = lines_total / minutes
    speed_score = _piecewise_linear(lines_per_minute, REACTION_LPM_FLOOR, REACTION_LPM_CEILING)
    score = REACTION_ACCURACY_WEIGHT * correct_ratio + REACTION_SPEED_WEIGHT * speed_score

    return ReactionResult(
        lines_correct=lines_correct,
        lines_total=lines_total,
        correct_ratio=correct_ratio,
        lines_per_minute=lines_per_minute,
        speed_score=speed_score,
        score=score,
    )

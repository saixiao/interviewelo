from app.elo.constants import STARTING_RATING
from app.models import QuizQuestion


def is_correct(selected_keys: list[str], correct_keys: list[str]) -> bool:
    """Exact-set match -- no partial credit per answer. Complexity screens
    score their time/space questions as two independent answers instead, so
    partial credit (nail time, miss space) falls out of the session average
    for free without any special-casing here."""
    return set(selected_keys) == set(correct_keys)


def overall_score(correctness: list[bool]) -> float:
    return sum(correctness) / len(correctness) if correctness else 0.0


def mean_difficulty(questions: list[QuizQuestion]) -> int:
    if not questions:
        return STARTING_RATING
    return round(sum(q.difficulty for q in questions) / len(questions))

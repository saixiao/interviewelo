"""Load all 3 quiz-mode question banks into the database.

Idempotent: clears existing quiz_questions and reinserts from the seed_data
modules. Run with: python -m app.quiz.seed
"""

import uuid

from app.db import SessionLocal
from app.models import QuizQuestion
from app.quiz.seed_data_complexity import SNIPPETS
from app.quiz.seed_data_python import QUESTIONS as PYTHON_QUESTIONS
from app.quiz.seed_data_systems import QUESTIONS as SYSTEMS_QUESTIONS


def _trivia_rows(category: str, questions) -> list[QuizQuestion]:
    return [
        QuizQuestion(
            category=category,
            topic=topic,
            difficulty=difficulty,
            prompt_md=prompt_md,
            choices=[{"key": key, "label": label} for key, label in choices],
            correct_keys=correct_keys,
            multi_select=multi_select,
            explanation_md=explanation_md,
        )
        for topic, difficulty, prompt_md, choices, correct_keys, multi_select, explanation_md in questions
    ]


def _complexity_rows(snippets) -> list[QuizQuestion]:
    rows: list[QuizQuestion] = []
    for difficulty, language, code, correct_time_key, correct_space_key, explanation_md in snippets:
        group_id = uuid.uuid4()
        rows.append(
            QuizQuestion(
                category="complexity",
                difficulty=difficulty,
                prompt_md="What is the time complexity of this code?",
                code_snippet=code,
                language=language,
                correct_keys=[correct_time_key],
                multi_select=False,
                dimension="time",
                group_id=group_id,
                explanation_md=explanation_md,
            )
        )
        rows.append(
            QuizQuestion(
                category="complexity",
                difficulty=difficulty,
                prompt_md="What is the space complexity of this code?",
                code_snippet=code,
                language=language,
                correct_keys=[correct_space_key],
                multi_select=False,
                dimension="space",
                group_id=group_id,
                explanation_md=explanation_md,
            )
        )
    return rows


def seed() -> int:
    db = SessionLocal()
    try:
        db.query(QuizQuestion).delete()
        rows = (
            _trivia_rows("python_trivia", PYTHON_QUESTIONS)
            + _trivia_rows("systems_trivia", SYSTEMS_QUESTIONS)
            + _complexity_rows(SNIPPETS)
        )
        db.add_all(rows)
        db.commit()
        return len(rows)
    finally:
        db.close()


if __name__ == "__main__":
    count = seed()
    print(f"Seeded {count} quiz questions")

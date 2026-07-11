"""Load the Approach Round prompt bank into the database.

Idempotent: clears existing approach_prompts and reinserts from seed_data.
Run with: python -m app.approach.seed
"""

from app.approach.seed_data import PROMPTS
from app.db import SessionLocal
from app.models import ApproachPrompt


def seed() -> int:
    db = SessionLocal()
    try:
        db.query(ApproachPrompt).delete()
        for title, difficulty, prompt_md, grading_notes_md in PROMPTS:
            db.add(
                ApproachPrompt(
                    title=title,
                    difficulty=difficulty,
                    prompt_md=prompt_md,
                    grading_notes_md=grading_notes_md,
                )
            )
        db.commit()
        return len(PROMPTS)
    finally:
        db.close()


if __name__ == "__main__":
    count = seed()
    print(f"Seeded {count} approach prompts")

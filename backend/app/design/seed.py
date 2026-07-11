"""Load the System Design prompt bank into the database.

Idempotent: clears existing design_prompts and reinserts from seed_data.
Run with: python -m app.design.seed
"""

from app.design.seed_data import PROMPTS
from app.db import SessionLocal
from app.models import DesignPrompt


def seed() -> int:
    db = SessionLocal()
    try:
        db.query(DesignPrompt).delete()
        for title, difficulty, prompt_md, rubric_md in PROMPTS:
            db.add(
                DesignPrompt(
                    title=title,
                    difficulty=difficulty,
                    prompt_md=prompt_md,
                    rubric_md=rubric_md,
                )
            )
        db.commit()
        return len(PROMPTS)
    finally:
        db.close()


if __name__ == "__main__":
    count = seed()
    print(f"Seeded {count} design prompts")

"""Load the Typing Racer snippet bank into the database.

Idempotent: clears existing typing_snippets and reinserts from seed_data.
Run with: python -m app.typing.seed
"""

from app.db import SessionLocal
from app.models import TypingSnippet
from app.typing.difficulty import difficulty_for
from app.typing.seed_data import SNIPPETS


def seed() -> int:
    db = SessionLocal()
    try:
        db.query(TypingSnippet).delete()
        for content in SNIPPETS:
            db.add(
                TypingSnippet(
                    content=content,
                    difficulty=difficulty_for(content),
                    char_count=len(content),
                    line_count=1,
                )
            )
        db.commit()
        return len(SNIPPETS)
    finally:
        db.close()


if __name__ == "__main__":
    count = seed()
    print(f"Seeded {count} typing snippets")

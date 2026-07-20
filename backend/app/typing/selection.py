"""Adaptive-difficulty snippet selection for Typing Racer.

Historically typing picked snippets uniformly at random and let the Elo
*scoring* math be the only place rating matters (see quiz/selection.py's
docstring for that contrast). Progressive-overload content now needs
selection itself to adapt too: a low-rated user should mostly see plain,
low-symbol-density lines, and shift/caps-heavy lines should only start
showing up as their typing rating climbs. Mirrors quiz/selection.py's
widening-window approach, but -- unlike quiz -- keeps typing's existing
"pad by repeating" behavior instead of excluding recently-seen content,
since typing has no memorizable "correct letter" to game.
"""

from uuid import UUID

from sqlalchemy.orm import Session

from app.elo.constants import STARTING_RATING
from app.elo.engine import category_ratings
from app.models import TypingSnippet

# Elo points either side of the user's current rating that the candidate
# pool draws from; widened (not narrowed) when too few snippets fall inside it.
INITIAL_WINDOW = 200
WINDOW_GROWTH = 2.0
MAX_WIDENINGS = 3


def candidate_snippets(db: Session, user_id: UUID) -> list[TypingSnippet]:
    """Snippets whose difficulty falls in a window centered on the user's
    current typing rating, widening until at least a handful are found (or
    the widenings run out, in which case fall back to the whole bank so a
    session never fails to start)."""
    ratings = category_ratings(db, user_id)
    rating = ratings["typing"].rating if "typing" in ratings else STARTING_RATING

    all_snippets = db.query(TypingSnippet).all()
    if not all_snippets:
        return []

    window = float(INITIAL_WINDOW)
    for attempt in range(MAX_WIDENINGS + 1):
        candidates = [s for s in all_snippets if rating - window <= s.difficulty <= rating + window]
        if len(candidates) >= 8 or attempt == MAX_WIDENINGS:
            break
        window *= WINDOW_GROWTH

    return candidates or all_snippets

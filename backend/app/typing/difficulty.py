"""Content-derived difficulty for typing snippets.

Progressive-overload feel: a snippet's difficulty is computed straight from
its own symbol density rather than hand-authored, so the "harder" bucket is
*guaranteed* to mean more unique characters and more shift/caps-requiring
keystrokes, not just an editor's guess. `select_queue` (selection.py) then
draws from a window centered on the user's rating, so low-Elo users are
mechanically fenced off from shift-heavy content until they climb.
"""

import string

# Characters that require holding Shift (or Caps Lock) on a standard US
# keyboard layout: all uppercase letters, plus the shift row of symbols.
SHIFT_CHARS = set(string.ascii_uppercase) | set('~!@#$%^&*()_+{}|:"<>?')

DIFFICULTY_FLOOR = 200
DIFFICULTY_CEILING = 3000

_BASE = 220
_PER_CHAR = 3
_PER_UNIQUE_CHAR = 18
_PER_SHIFT_CHAR = 40


def difficulty_for(content: str) -> int:
    """Map a single line of code to an Elo-scale difficulty rating.

    Weighted so shift/caps-requiring characters (the "progressive overload"
    axis) dominate over raw length -- two lines of equal length differ in
    difficulty mainly by how much Shift they demand.
    """
    length = len(content)
    unique_chars = len(set(content))
    shift_chars = sum(1 for c in content if c in SHIFT_CHARS)

    raw = _BASE + _PER_CHAR * length + _PER_UNIQUE_CHAR * unique_chars + _PER_SHIFT_CHAR * shift_chars
    return max(DIFFICULTY_FLOOR, min(DIFFICULTY_CEILING, round(raw)))

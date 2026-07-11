"""Fixed choice list for the complexity-analysis quiz category, plus the
category slugs this module recognizes. Big-O choices are centralized here
rather than duplicated on every quiz_questions row."""

QUIZ_CATEGORIES = ("python_trivia", "systems_trivia", "complexity")

BIG_O_CHOICES: list[tuple[str, str]] = [
    ("o1", "O(1)"),
    ("olog_n", "O(log n)"),
    ("on", "O(n)"),
    ("on_log_n", "O(n log n)"),
    ("on2", "O(n²)"),
    ("on3", "O(n³)"),
    ("o2n", "O(2ⁿ)"),
    ("on_fact", "O(n!)"),
]

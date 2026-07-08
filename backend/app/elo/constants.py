MIN_RATING = 0
MAX_RATING = 3000
STARTING_RATING = 500

PLACEMENT_SESSIONS = 10
PLACEMENT_K = 40
STANDARD_K = 24

# Elo "sensitivity" divisor in the expected-score logistic curve. Larger = flatter
# (skill gaps matter less); 400 mirrors standard chess Elo.
ELO_SPREAD = 400

CATEGORIES = ("typing", "coding", "approach", "design")

# (tier name, inclusive lower bound) ordered ascending; upper bound is the next
# tier's lower bound minus 1, and the last tier runs to MAX_RATING.
TIERS: list[tuple[str, int]] = [
    ("Noob", 0),
    ("Intern", 300),
    ("Entry Level", 600),
    ("Mid Level", 900),
    ("Senior", 1200),
    ("Staff", 1500),
    ("Sr. Staff", 1800),
    ("Principal", 2100),
    ("Fellow", 2400),
    ("AGI", 2700),
]

# Both modes' speed curves (WPM for Classic, lines-per-minute for Reaction)
# scale their floor/ceiling with the difficulty of the content actually
# typed, not a fixed number -- since queue selection (selection.py) already
# hands harder, more shift/symbol-dense content to higher-rated users, the
# bar for a top score should climb right along with it ("progressive
# overload" applies to grading, not just content). At difficulty 0 the
# *_BASE values apply; at DIFFICULTY_CEILING (3000, difficulty.py) the
# *_MAX values apply; difficulty.py's difficulty_for() also caps at 3000
# well before which no snippet in the seeded bank(see seed_data.py) is that
# hard, so the curve never quite reaches the harshest end in practice.
CLASSIC_WPM_FLOOR_BASE = 12.0
CLASSIC_WPM_FLOOR_MAX = 25.0
CLASSIC_WPM_CEILING_BASE = 45.0
CLASSIC_WPM_CEILING_MAX = 95.0

REACTION_LPM_FLOOR_BASE = 3.0
REACTION_LPM_FLOOR_MAX = 6.0
REACTION_LPM_CEILING_BASE = 14.0
REACTION_LPM_CEILING_MAX = 26.0

# Coding-interview accuracy matters far more than raw speed -- a fast typist
# who fat-fingers a symbol under pressure is worse off in a real interview
# than someone slower but exact. Both modes score as a weighted blend of
# accuracy and a speed_score (rather than accuracy multiplying speed, which
# punished any typo quadratically and made speed the only way to recover).
CLASSIC_ACCURACY_WEIGHT = 0.7
CLASSIC_SPEED_WEIGHT = 0.3

REACTION_ACCURACY_WEIGHT = 0.7
REACTION_SPEED_WEIGHT = 0.3

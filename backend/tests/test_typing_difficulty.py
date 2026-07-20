from app.typing.difficulty import DIFFICULTY_CEILING, DIFFICULTY_FLOOR, difficulty_for


def test_plain_alnum_line_is_low_difficulty():
    assert difficulty_for("total = 0") < 600


def test_shift_heavy_line_is_high_difficulty():
    assert difficulty_for('headers = {"Authorization": f"Bearer {token}"}') > 1100


def test_uppercase_letters_count_as_shift_characters():
    lower = difficulty_for("result = value")
    upper = difficulty_for("RESULT = VALUE")
    assert upper > lower


def test_adding_shift_symbols_increases_difficulty_at_fixed_length():
    base = "x = (1 2)"
    with_shift_symbols = "x = {1|2}"
    assert len(base) == len(with_shift_symbols)
    assert difficulty_for(with_shift_symbols) > difficulty_for(base)


def test_difficulty_is_clamped_to_valid_elo_range():
    assert difficulty_for("x") >= DIFFICULTY_FLOOR
    huge = "x" * 2000 + "".join(chr(33 + i % 94) for i in range(2000))
    assert difficulty_for(huge) <= DIFFICULTY_CEILING

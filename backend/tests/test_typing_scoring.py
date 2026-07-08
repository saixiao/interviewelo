import pytest

from app.typing.scoring import ClassicItem, score_classic_attempt, score_reaction_attempt


def test_classic_perfect_typing_full_accuracy():
    items = [ClassicItem(target="hello world", typed="hello world")]
    result = score_classic_attempt(items, elapsed_s=60)
    assert result.accuracy == 1.0
    assert result.raw_wpm == pytest.approx((11 / 5) / 1)
    assert result.net_wpm == result.raw_wpm


def test_classic_typos_reduce_accuracy_and_net_wpm():
    items = [ClassicItem(target="hello world", typed="hxllo worlx")]
    result = score_classic_attempt(items, elapsed_s=60)
    assert 0 < result.accuracy < 1.0
    assert result.net_wpm < result.raw_wpm


def test_classic_undertyping_and_overtyping_both_penalized():
    short = score_classic_attempt([ClassicItem(target="hello world", typed="hello")], elapsed_s=60)
    long_ = score_classic_attempt([ClassicItem(target="hello", typed="hello world")], elapsed_s=60)
    assert short.accuracy < 1.0
    assert long_.accuracy < 1.0


def test_classic_score_zero_below_floor_wpm():
    # 1 char typed in 60s is far below the 20 net-wpm floor
    result = score_classic_attempt([ClassicItem(target="x", typed="x")], elapsed_s=60)
    assert result.score == 0.0


def test_classic_score_one_above_ceiling_wpm():
    fast_text = "the quick brown fox jumps over " * 10  # plenty of words
    result = score_classic_attempt([ClassicItem(target=fast_text, typed=fast_text)], elapsed_s=10)
    assert result.score == 1.0


def test_classic_score_is_monotonic_in_net_wpm():
    slow = score_classic_attempt([ClassicItem(target="a" * 20, typed="a" * 20)], elapsed_s=60)
    fast = score_classic_attempt([ClassicItem(target="a" * 20, typed="a" * 20)], elapsed_s=6)
    assert fast.score >= slow.score


def test_classic_empty_items_scores_zero():
    result = score_classic_attempt([], elapsed_s=60)
    assert result.score == 0.0
    assert result.accuracy == 1.0


def test_classic_rejects_non_positive_elapsed():
    with pytest.raises(ValueError):
        score_classic_attempt([ClassicItem("a", "a")], elapsed_s=0)


def test_reaction_all_correct_full_ratio():
    result = score_reaction_attempt([True, True, True, True], elapsed_s=60)
    assert result.correct_ratio == 1.0
    assert result.lines_correct == 4
    assert result.lines_total == 4


def test_reaction_mixed_correctness_partial_ratio():
    result = score_reaction_attempt([True, False, True, False], elapsed_s=60)
    assert result.correct_ratio == 0.5


def test_reaction_accuracy_weighted_higher_than_speed():
    # A full swing from max to min speed_score (lpm from ceiling to floor)
    # should cost less than a full swing from max to min correct_ratio,
    # since accuracy's weight (0.7) exceeds speed's (0.3).
    perfect_and_fast = score_reaction_attempt([True] * 20, elapsed_s=60)  # lpm=20 (ceiling)
    perfect_and_slow = score_reaction_attempt([True] * 4, elapsed_s=60)  # lpm=4 (floor)
    zero_correct_and_fast = score_reaction_attempt([False] * 20, elapsed_s=60)

    assert perfect_and_fast.score == pytest.approx(1.0)
    drop_from_slow_speed = perfect_and_fast.score - perfect_and_slow.score
    drop_from_zero_accuracy = perfect_and_fast.score - zero_correct_and_fast.score
    assert drop_from_zero_accuracy > drop_from_slow_speed


def test_reaction_no_lines_scores_zero():
    result = score_reaction_attempt([], elapsed_s=60)
    assert result.score == 0.0
    assert result.correct_ratio == 0.0


def test_reaction_rejects_non_positive_elapsed():
    with pytest.raises(ValueError):
        score_reaction_attempt([True], elapsed_s=0)

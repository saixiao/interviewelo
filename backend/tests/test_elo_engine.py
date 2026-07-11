import uuid

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db import Base
from app.elo.constants import STARTING_RATING
from app.elo.engine import apply_session_result, expected_score, k_factor, tier_for
from app.models import EloHistory, UserRating  # noqa: F401 (register mappers)


@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session = Session(engine)
    yield session
    session.close()


@pytest.mark.parametrize(
    "rating,expected_tier",
    [
        (0, "Noob"),
        (299, "Noob"),
        (300, "Intern"),
        (599, "Intern"),
        (600, "Entry Level"),
        (1199, "Mid Level"),
        (1200, "Senior"),
        (2699, "Fellow"),
        (2700, "AGI"),
        (3000, "AGI"),
    ],
)
def test_tier_for_boundaries(rating, expected_tier):
    assert tier_for(rating) == expected_tier


def test_tier_for_clamps_out_of_range():
    assert tier_for(-500) == "Noob"
    assert tier_for(5000) == "AGI"


def test_expected_score_is_half_at_equal_rating():
    assert expected_score(1000, 1000) == pytest.approx(0.5)


def test_expected_score_favors_higher_rating():
    assert expected_score(1400, 1000) > 0.5
    assert expected_score(1000, 1400) < 0.5


def test_k_factor_placement_then_standard():
    assert k_factor(0) == 40
    assert k_factor(9) == 40
    assert k_factor(10) == 24
    assert k_factor(100) == 24


def test_apply_session_result_creates_rating_at_starting_value(db):
    user_id = uuid.uuid4()
    result = apply_session_result(
        db, user_id, "typing", score=0.5, difficulty=STARTING_RATING, source_type="typing_attempt"
    )
    # score == expected at equal rating/difficulty, so delta should be ~0
    assert result.rating_before == STARTING_RATING
    assert result.delta == 0
    assert result.tier_before == "Intern"


def test_apply_session_result_beats_expectation_increases_rating(db):
    user_id = uuid.uuid4()
    result = apply_session_result(
        db, user_id, "design", score=1.0, difficulty=STARTING_RATING, source_type="submission"
    )
    assert result.delta > 0
    assert result.rating_after > result.rating_before


def test_apply_session_result_below_expectation_decreases_rating(db):
    user_id = uuid.uuid4()
    result = apply_session_result(
        db, user_id, "design", score=0.0, difficulty=STARTING_RATING, source_type="submission"
    )
    assert result.delta < 0
    assert result.rating_after < result.rating_before


def test_apply_session_result_persists_and_accumulates(db):
    user_id = uuid.uuid4()
    apply_session_result(db, user_id, "typing", score=1.0, difficulty=500, source_type="typing_attempt")
    second = apply_session_result(db, user_id, "typing", score=1.0, difficulty=500, source_type="typing_attempt")

    rating_row = db.query(UserRating).filter_by(user_id=user_id, category="typing").one()
    assert rating_row.sessions_count == 2
    assert rating_row.rating == second.rating_after

    history = db.query(EloHistory).filter_by(user_id=user_id, category="typing").all()
    assert len(history) == 2


def test_apply_session_result_rejects_out_of_range_score(db):
    with pytest.raises(ValueError):
        apply_session_result(db, uuid.uuid4(), "typing", score=1.5, difficulty=500, source_type="typing_attempt")


def test_rating_clamped_to_max(db):
    user_id = uuid.uuid4()
    result = None
    for _ in range(200):
        result = apply_session_result(
            db, user_id, "design", score=1.0, difficulty=3000, source_type="design_session"
        )
    assert result.rating_after <= 3000

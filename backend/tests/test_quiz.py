import uuid

from app.elo.constants import STARTING_RATING
from app.models import QuizAnswer, QuizQuestion, QuizSession, User, UserRating
from app.quiz.selection import INITIAL_WINDOW, MAX_WIDENINGS, select_queue


def _auth_headers(client, email="quizzer@example.com"):
    resp = client.post(
        "/auth/signup",
        json={"email": email, "password": "hunter2222", "display_name": "Quizzer"},
    )
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def _add_trivia_question(
    db_session, category="python_trivia", difficulty=500, topic="t", correct=("a",), multi=False
) -> QuizQuestion:
    q = QuizQuestion(
        category=category,
        topic=topic,
        difficulty=difficulty,
        prompt_md="Q?",
        choices=[{"key": "a", "label": "A"}, {"key": "b", "label": "B"}],
        correct_keys=list(correct),
        multi_select=multi,
        explanation_md="Because.",
    )
    db_session.add(q)
    db_session.commit()
    db_session.refresh(q)
    return q


def _add_complexity_pair(db_session, difficulty=500, correct_time="on", correct_space="o1"):
    group_id = uuid.uuid4()
    time_q = QuizQuestion(
        category="complexity",
        difficulty=difficulty,
        prompt_md="What is the time complexity of this code?",
        code_snippet="pass",
        language="python",
        correct_keys=[correct_time],
        multi_select=False,
        dimension="time",
        group_id=group_id,
        explanation_md="Because.",
    )
    space_q = QuizQuestion(
        category="complexity",
        difficulty=difficulty,
        prompt_md="What is the space complexity of this code?",
        code_snippet="pass",
        language="python",
        correct_keys=[correct_space],
        multi_select=False,
        dimension="space",
        group_id=group_id,
        explanation_md="Because.",
    )
    db_session.add_all([time_q, space_q])
    db_session.commit()
    db_session.refresh(time_q)
    db_session.refresh(space_q)
    return time_q, space_q


# --- select_queue: adaptive difficulty --------------------------------------


def test_select_queue_stays_near_starting_rating_by_default(db_session):
    for d in (400, 500, 600, 2500):
        _add_trivia_question(db_session, difficulty=d)
    chosen = select_queue(db_session, uuid.uuid4(), "python_trivia", target_count=10)
    difficulties = {q.difficulty for q in chosen}
    assert difficulties == {400, 500, 600}  # 2500 is far outside the initial window around 500


def test_select_queue_widens_window_when_bank_is_thin(db_session):
    _add_trivia_question(db_session, difficulty=STARTING_RATING)
    # Just inside the range reached after MAX_WIDENINGS doublings of INITIAL_WINDOW.
    far = STARTING_RATING + INITIAL_WINDOW * (2**MAX_WIDENINGS) - 10
    _add_trivia_question(db_session, difficulty=far)
    chosen = select_queue(db_session, uuid.uuid4(), "python_trivia", target_count=5)
    assert len(chosen) == 2


def test_select_queue_excludes_recently_answered(db_session):
    q1 = _add_trivia_question(db_session, difficulty=500)
    q2 = _add_trivia_question(db_session, difficulty=500)
    user_id = uuid.uuid4()

    session = QuizSession(
        user_id=user_id, category="python_trivia", duration_s=180, elapsed_s=100, overall_score=1.0, elo_delta=0
    )
    db_session.add(session)
    db_session.flush()
    db_session.add(QuizAnswer(session_id=session.id, question_id=q1.id, selected_keys=["a"], correct=True))
    db_session.commit()

    chosen = select_queue(db_session, user_id, "python_trivia", target_count=5)
    chosen_ids = {q.id for q in chosen}
    assert q1.id not in chosen_ids
    assert q2.id in chosen_ids


def test_select_queue_complexity_returns_time_then_space_pairs(db_session):
    _add_complexity_pair(db_session, difficulty=500)
    chosen = select_queue(db_session, uuid.uuid4(), "complexity", target_count=1)
    assert len(chosen) == 2
    assert chosen[0].dimension == "time"
    assert chosen[1].dimension == "space"
    assert chosen[0].group_id == chosen[1].group_id


def _set_rating(db_session, user_id, category, rating, sessions_count=15):
    """Directly seed a UserRating row, bypassing apply_session_result, so a
    test can pin a user at an exact rating without playing dozens of sessions."""
    db_session.add(UserRating(user_id=user_id, category=category, rating=rating, sessions_count=sessions_count))
    db_session.commit()


def test_select_queue_difficulty_tracks_rating_low_mid_high(db_session):
    """The core adaptive-difficulty guarantee: a Noob-rated user, an
    Intern-rated (default) user, and an AGI-rated user each get a queue
    whose average difficulty is close to their own rating, strictly
    increasing as rating increases -- this is what "harder questions as
    Elo increases" means concretely.

    Seeded densely enough (every 50 points) that the *initial* window alone
    -- no widening -- already covers target_count candidates at every rating
    tested, so the resulting average is a direct readout of the unwidened
    +-INITIAL_WINDOW band, not a widened fallback.
    """
    for d in range(100, 2901, 50):
        _add_trivia_question(db_session, difficulty=d)

    noob = uuid.uuid4()
    _set_rating(db_session, noob, "python_trivia", rating=150)

    intern = uuid.uuid4()
    _set_rating(db_session, intern, "python_trivia", rating=STARTING_RATING)

    agi = uuid.uuid4()
    _set_rating(db_session, agi, "python_trivia", rating=2850)

    def avg_difficulty(user_id, rating):
        chosen = select_queue(db_session, user_id, "python_trivia", target_count=4)
        assert len(chosen) == 4  # confirms this ran off the initial window, not a widened one
        avg = sum(q.difficulty for q in chosen) / len(chosen)
        assert abs(avg - rating) <= INITIAL_WINDOW
        return avg

    noob_avg = avg_difficulty(noob, 150)
    intern_avg = avg_difficulty(intern, STARTING_RATING)
    agi_avg = avg_difficulty(agi, 2850)

    assert noob_avg < intern_avg < agi_avg


def test_select_queue_never_serves_far_below_a_high_raters_level(db_session):
    """A high-rated user shouldn't be handed a queue dominated by trivially
    easy content just because easy content exists in the bank."""
    _add_trivia_question(db_session, difficulty=300)
    _add_trivia_question(db_session, difficulty=2600)
    _add_trivia_question(db_session, difficulty=2700)

    high_rater = uuid.uuid4()
    _set_rating(db_session, high_rater, "python_trivia", rating=2650)

    chosen = select_queue(db_session, high_rater, "python_trivia", target_count=5)
    difficulties = {q.difficulty for q in chosen}
    assert 300 not in difficulties
    assert difficulties == {2600, 2700}


# --- API: queue --------------------------------------------------------------


def test_queue_requires_auth(client):
    resp = client.get("/quiz/python_trivia/queue")
    assert resp.status_code == 401


def test_queue_unknown_category_rejected(client):
    headers = _auth_headers(client)
    resp = client.get("/quiz/not_a_category/queue", headers=headers)
    assert resp.status_code == 404


def test_queue_without_questions_returns_503(client):
    headers = _auth_headers(client)
    resp = client.get("/quiz/python_trivia/queue", headers=headers)
    assert resp.status_code == 503


def test_queue_endpoint_serves_harder_questions_to_higher_rated_users(client, db_session):
    """End-to-end proof (through the real HTTP endpoint, not just the
    internal select_queue function) that GET /quiz/{category}/queue reflects
    the authenticated user's own rating."""
    for d in range(200, 2801, 200):
        _add_trivia_question(db_session, difficulty=d)

    low_headers = _auth_headers(client, email="low_rater@example.com")
    low_user = db_session.query(User).filter_by(email="low_rater@example.com").one()
    _set_rating(db_session, low_user.id, "python_trivia", rating=300)

    high_headers = _auth_headers(client, email="high_rater@example.com")
    high_user = db_session.query(User).filter_by(email="high_rater@example.com").one()
    _set_rating(db_session, high_user.id, "python_trivia", rating=2500)

    low_resp = client.get("/quiz/python_trivia/queue?duration_s=300", headers=low_headers)
    high_resp = client.get("/quiz/python_trivia/queue?duration_s=300", headers=high_headers)
    assert low_resp.status_code == 200
    assert high_resp.status_code == 200

    low_difficulties = [q["difficulty"] for q in low_resp.json()["questions"]]
    high_difficulties = [q["difficulty"] for q in high_resp.json()["questions"]]
    assert (sum(low_difficulties) / len(low_difficulties)) < (sum(high_difficulties) / len(high_difficulties))
    # The low rater should never see the hardest content and vice versa.
    assert max(low_difficulties) < min(high_difficulties)


def test_queue_never_leaks_answers(client, db_session):
    _add_trivia_question(db_session, difficulty=500)
    headers = _auth_headers(client)
    resp = client.get("/quiz/python_trivia/queue", headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    assert len(body["questions"]) >= 1
    for q in body["questions"]:
        assert "correct_keys" not in q
        assert "explanation_md" not in q


def test_queue_complexity_uses_shared_big_o_choices(client, db_session):
    _add_complexity_pair(db_session, difficulty=500)
    headers = _auth_headers(client)
    resp = client.get("/quiz/complexity/queue", headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    assert len(body["questions"]) == 2
    labels = {c["label"] for c in body["questions"][0]["choices"]}
    assert "O(n)" in labels
    assert "O(1)" in labels


# --- API: attempts -------------------------------------------------------------


def test_submit_attempt_requires_auth(client):
    resp = client.post("/quiz/python_trivia/attempts", json={"duration_s": 180, "elapsed_s": 60, "answers": []})
    assert resp.status_code == 401


def test_submit_attempt_rejects_empty_answers(client):
    headers = _auth_headers(client)
    resp = client.post(
        "/quiz/python_trivia/attempts",
        headers=headers,
        json={"duration_s": 180, "elapsed_s": 60, "answers": []},
    )
    assert resp.status_code == 400


def test_submit_attempt_rejects_unknown_question_id(client):
    headers = _auth_headers(client)
    resp = client.post(
        "/quiz/python_trivia/attempts",
        headers=headers,
        json={
            "duration_s": 180,
            "elapsed_s": 60,
            "answers": [{"question_id": str(uuid.uuid4()), "selected_keys": ["a"]}],
        },
    )
    assert resp.status_code == 400


def test_submit_attempt_all_correct_increases_rating(client, db_session):
    q1 = _add_trivia_question(db_session, difficulty=800, correct=("a",))
    q2 = _add_trivia_question(db_session, difficulty=800, correct=("a",))
    headers = _auth_headers(client)
    resp = client.post(
        "/quiz/python_trivia/attempts",
        headers=headers,
        json={
            "duration_s": 180,
            "elapsed_s": 60,
            "answers": [
                {"question_id": str(q1.id), "selected_keys": ["a"]},
                {"question_id": str(q2.id), "selected_keys": ["a"]},
            ],
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["overall_score"] == 1.0
    assert body["delta"] > 0
    assert all(r["correct"] for r in body["results"])


def test_submit_attempt_all_wrong_decreases_rating(client, db_session):
    q1 = _add_trivia_question(db_session, difficulty=200, correct=("a",))
    headers = _auth_headers(client)
    resp = client.post(
        "/quiz/python_trivia/attempts",
        headers=headers,
        json={
            "duration_s": 180,
            "elapsed_s": 60,
            "answers": [{"question_id": str(q1.id), "selected_keys": ["b"]}],
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["overall_score"] == 0.0
    assert body["delta"] < 0


def test_submit_attempt_select_all_requires_exact_set_match(client, db_session):
    q = _add_trivia_question(db_session, difficulty=500, correct=("a", "c"), multi=True)
    headers = _auth_headers(client)
    resp = client.post(
        "/quiz/python_trivia/attempts",
        headers=headers,
        json={
            "duration_s": 180,
            "elapsed_s": 60,
            "answers": [{"question_id": str(q.id), "selected_keys": ["a"]}],  # missing "c"
        },
    )
    assert resp.status_code == 200
    assert resp.json()["results"][0]["correct"] is False


def test_submit_attempt_complexity_partial_credit_averages_dimensions(client, db_session):
    time_q, space_q = _add_complexity_pair(db_session, difficulty=500, correct_time="on", correct_space="o1")
    headers = _auth_headers(client)
    resp = client.post(
        "/quiz/complexity/attempts",
        headers=headers,
        json={
            "duration_s": 180,
            "elapsed_s": 60,
            "answers": [
                {"question_id": str(time_q.id), "selected_keys": ["on"]},  # correct
                {"question_id": str(space_q.id), "selected_keys": ["on2"]},  # wrong
            ],
        },
    )
    assert resp.status_code == 200
    assert resp.json()["overall_score"] == 0.5

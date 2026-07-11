import uuid

from app.elo.constants import STARTING_RATING
from app.models import QuizAnswer, QuizQuestion, QuizSession
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

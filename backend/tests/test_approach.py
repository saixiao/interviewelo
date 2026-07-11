from unittest.mock import patch

from app.llm.grader import AnswerGrade, SessionGrade
from app.models import ApproachPrompt


def _auth_headers(client):
    resp = client.post(
        "/auth/signup",
        json={"email": "approacher@example.com", "password": "hunter2222", "display_name": "Approacher"},
    )
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def _add_prompt(db_session, title: str, difficulty: int = 900) -> ApproachPrompt:
    prompt = ApproachPrompt(
        title=title,
        difficulty=difficulty,
        prompt_md=f"Solve {title}.",
        grading_notes_md=f"The intended approach for {title}.",
    )
    db_session.add(prompt)
    db_session.commit()
    db_session.refresh(prompt)
    return prompt


def _fake_grade(n: int, score: int = 80) -> SessionGrade:
    return SessionGrade(
        answers=[
            AnswerGrade(
                approach_correctness=score,
                complexity_awareness=score,
                edge_case_awareness=score,
                communication=score,
                feedback="Solid approach, minor gaps.",
            )
            for _ in range(n)
        ],
        session_summary="Consistently strong across all questions.",
    )


def test_queue_requires_auth(client):
    resp = client.get("/approach/queue")
    assert resp.status_code == 401


def test_queue_without_prompts_returns_503(client):
    headers = _auth_headers(client)
    resp = client.get("/approach/queue", headers=headers)
    assert resp.status_code == 503


def test_queue_returns_up_to_five_prompts(client, db_session):
    for i in range(8):
        _add_prompt(db_session, f"Prompt {i}")
    headers = _auth_headers(client)

    resp = client.get("/approach/queue", headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    assert len(body["items"]) == 5
    assert all({"prompt_id", "title", "prompt_md"} <= item.keys() for item in body["items"])
    # grading_notes_md must never leave the server
    assert all("grading_notes_md" not in item for item in body["items"])


def test_queue_returns_fewer_than_five_if_pool_is_smaller(client, db_session):
    _add_prompt(db_session, "Only One")
    headers = _auth_headers(client)

    resp = client.get("/approach/queue", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()["items"]) == 1


def test_queue_respects_count_param(client, db_session):
    for i in range(8):
        _add_prompt(db_session, f"Prompt {i}")
    headers = _auth_headers(client)

    resp = client.get("/approach/queue", params={"count": 1}, headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()["items"]) == 1


def test_submit_infinite_attempt_does_not_affect_elo(client, db_session):
    prompt = _add_prompt(db_session, "Solo Prompt", difficulty=900)
    headers = _auth_headers(client)

    before = client.get("/me", headers=headers).json()
    approach_before = next(c for c in before["categories"] if c["category"] == "approach")
    assert approach_before["rating"] == 500

    with patch("app.approach.router.grade_session", return_value=_fake_grade(1, score=95)):
        resp = client.post(
            "/approach/attempts",
            headers=headers,
            json={
                "elapsed_s": 30,
                "items": [{"prompt_id": str(prompt.id), "answer_text": "A great approach"}],
                "is_infinite": True,
            },
        )

    assert resp.status_code == 200
    body = resp.json()
    assert body["score"] == 0.95
    assert body["delta"] == 0
    assert body["rating_before"] == body["rating_after"] == 500

    after = client.get("/me", headers=headers).json()
    approach_after = next(c for c in after["categories"] if c["category"] == "approach")
    assert approach_after["rating"] == 500
    assert approach_after["sessions_count"] == 0


def test_submit_attempt_grades_scores_and_updates_elo(client, db_session):
    prompts = [_add_prompt(db_session, f"Prompt {i}", difficulty=900) for i in range(3)]
    headers = _auth_headers(client)

    before = client.get("/me", headers=headers).json()
    approach_before = next(c for c in before["categories"] if c["category"] == "approach")
    assert approach_before["rating"] == 500

    with patch("app.approach.router.grade_session", return_value=_fake_grade(3, score=90)):
        resp = client.post(
            "/approach/attempts",
            headers=headers,
            json={
                "elapsed_s": 240,
                "items": [{"prompt_id": str(p.id), "answer_text": f"My approach for {p.title}"} for p in prompts],
            },
        )

    assert resp.status_code == 200
    body = resp.json()
    assert body["score"] == 0.9
    assert len(body["results"]) == 3
    assert body["results"][0]["approach_correctness"] == 90
    assert body["results"][0]["feedback"] == "Solid approach, minor gaps."
    assert body["session_summary"] == "Consistently strong across all questions."
    assert body["rating_after"] > body["rating_before"]
    assert body["delta"] > 0

    after = client.get("/me", headers=headers).json()
    approach_after = next(c for c in after["categories"] if c["category"] == "approach")
    assert approach_after["sessions_count"] == 1
    assert approach_after["rating"] == body["rating_after"]


def test_submit_attempt_rejects_unknown_prompt_id(client, db_session):
    headers = _auth_headers(client)
    resp = client.post(
        "/approach/attempts",
        headers=headers,
        json={
            "elapsed_s": 60,
            "items": [{"prompt_id": "00000000-0000-0000-0000-000000000000", "answer_text": "whatever"}],
        },
    )
    assert resp.status_code == 400


def test_submit_attempt_without_items_rejected(client, db_session):
    headers = _auth_headers(client)
    resp = client.post("/approach/attempts", headers=headers, json={"elapsed_s": 60, "items": []})
    assert resp.status_code == 400


def test_submit_attempt_returns_502_on_grading_failure(client, db_session):
    prompt = _add_prompt(db_session, "Flaky Prompt")
    headers = _auth_headers(client)

    with patch("app.approach.router.grade_session", side_effect=ValueError("boom")):
        resp = client.post(
            "/approach/attempts",
            headers=headers,
            json={"elapsed_s": 60, "items": [{"prompt_id": str(prompt.id), "answer_text": "an answer"}]},
        )

    assert resp.status_code == 502

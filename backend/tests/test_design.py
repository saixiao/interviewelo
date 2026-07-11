from unittest.mock import patch

from app.llm.grader import DesignGrade
from app.models import DesignPrompt, DesignSession


def _auth_headers(client, email: str = "designer@example.com"):
    resp = client.post(
        "/auth/signup",
        json={"email": email, "password": "hunter2222", "display_name": "Designer"},
    )
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def _add_prompt(db_session, title: str = "URL Shortener", difficulty: int = 900) -> DesignPrompt:
    prompt = DesignPrompt(
        title=title,
        difficulty=difficulty,
        prompt_md=f"Design {title}. 100M requests/day, p99 < 50ms.",
        rubric_md=f"SECRET RUBRIC for {title}: a strong answer covers X, Y, Z.",
    )
    db_session.add(prompt)
    db_session.commit()
    db_session.refresh(prompt)
    return prompt


def _create_session(client, headers, duration_s: int = 1200) -> dict:
    resp = client.post("/design/sessions", headers=headers, json={"duration_s": duration_s})
    assert resp.status_code == 200
    return resp.json()


def _fake_grade(overall: int = 72) -> DesignGrade:
    return DesignGrade(
        requirements=70,
        high_level_design=75,
        deep_dives=68,
        tradeoffs_and_scaling=74,
        strengths=["Clear component breakdown", "Cache in front of the store"],
        improvements=["Never addressed short-code collisions", "No story for the p99 target"],
        overall=overall,
    )


def test_rubric_requires_auth(client):
    assert client.get("/design/rubric").status_code == 401


def test_rubric_returns_four_dimensions(client):
    headers = _auth_headers(client)
    resp = client.get("/design/rubric", headers=headers)
    assert resp.status_code == 200
    dims = resp.json()
    assert [d["key"] for d in dims] == [
        "requirements",
        "high_level_design",
        "deep_dives",
        "tradeoffs_and_scaling",
    ]
    assert all({"key", "label", "description"} <= d.keys() for d in dims)


def test_create_session_requires_auth(client):
    assert client.post("/design/sessions", json={"duration_s": 1200}).status_code == 401


def test_create_session_without_prompts_returns_503(client):
    headers = _auth_headers(client)
    resp = client.post("/design/sessions", headers=headers, json={"duration_s": 1200})
    assert resp.status_code == 503


def test_create_session_returns_prompt_without_rubric(client, db_session):
    _add_prompt(db_session)
    headers = _auth_headers(client)

    body = _create_session(client, headers)
    assert body["duration_s"] == 1200
    assert body["prompt"]["title"] == "URL Shortener"
    assert "prompt_md" in body["prompt"]
    assert "difficulty" in body["prompt"]
    # rubric_md must never leave the server
    assert "rubric_md" not in body["prompt"]
    assert "SECRET RUBRIC" not in resp_text(body)


def resp_text(body) -> str:
    import json

    return json.dumps(body)


def test_get_session_state_supports_resume(client, db_session):
    _add_prompt(db_session)
    headers = _auth_headers(client)
    created = _create_session(client, headers, duration_s=1800)

    resp = client.get(f"/design/sessions/{created['session_id']}", headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "in_progress"
    assert body["duration_s"] == 1800
    assert 0 < body["remaining_s"] <= 1800
    assert body["follow_ups_used"] == 0
    assert body["transcript"] == []
    assert "rubric_md" not in resp_text(body)


def test_get_session_of_other_user_is_404(client, db_session):
    _add_prompt(db_session)
    owner = _auth_headers(client, email="owner@example.com")
    created = _create_session(client, owner)

    intruder = _auth_headers(client, email="intruder@example.com")
    resp = client.get(f"/design/sessions/{created['session_id']}", headers=intruder)
    assert resp.status_code == 404


def test_post_message_appends_and_persists(client, db_session):
    _add_prompt(db_session)
    headers = _auth_headers(client)
    created = _create_session(client, headers)
    sid = created["session_id"]

    resp = client.post(f"/design/sessions/{sid}/messages", headers=headers, json={"text": "I'd start with the API."})
    assert resp.status_code == 200
    body = resp.json()
    assert body["entry"]["role"] == "user"
    assert body["entry"]["text"] == "I'd start with the API."
    assert len(body["transcript"]) == 1

    resp2 = client.post(f"/design/sessions/{sid}/messages", headers=headers, json={"text": "Then the data model."})
    assert len(resp2.json()["transcript"]) == 2

    # persisted server-side, not just echoed
    session = db_session.query(DesignSession).one()
    assert [e["text"] for e in session.transcript] == ["I'd start with the API.", "Then the data model."]


def test_post_empty_message_rejected(client, db_session):
    _add_prompt(db_session)
    headers = _auth_headers(client)
    sid = _create_session(client, headers)["session_id"]

    resp = client.post(f"/design/sessions/{sid}/messages", headers=headers, json={"text": "   "})
    assert resp.status_code == 400


def test_follow_up_appends_interviewer_turn(client, db_session):
    _add_prompt(db_session)
    headers = _auth_headers(client)
    sid = _create_session(client, headers)["session_id"]

    client.post(f"/design/sessions/{sid}/messages", headers=headers, json={"text": "Hash the URL to a short code."})

    with patch("app.design.router.generate_design_followup", return_value="How do you handle collisions?"):
        resp = client.post(f"/design/sessions/{sid}/follow-up", headers=headers)

    assert resp.status_code == 200
    body = resp.json()
    assert body["entry"]["role"] == "interviewer"
    assert body["entry"]["text"] == "How do you handle collisions?"
    assert body["follow_ups_used"] == 1
    assert body["follow_ups_remaining"] == 4

    session = db_session.query(DesignSession).one()
    assert session.transcript[-1]["role"] == "interviewer"


def test_follow_up_capped_at_five(client, db_session):
    _add_prompt(db_session)
    headers = _auth_headers(client)
    sid = _create_session(client, headers)["session_id"]

    with patch("app.design.router.generate_design_followup", return_value="Probing question?"):
        for i in range(5):
            resp = client.post(f"/design/sessions/{sid}/follow-up", headers=headers)
            assert resp.status_code == 200
            assert resp.json()["follow_ups_used"] == i + 1

        resp = client.post(f"/design/sessions/{sid}/follow-up", headers=headers)
    assert resp.status_code == 409


def test_follow_up_returns_502_on_llm_failure(client, db_session):
    _add_prompt(db_session)
    headers = _auth_headers(client)
    sid = _create_session(client, headers)["session_id"]

    with patch("app.design.router.generate_design_followup", side_effect=ValueError("boom")):
        resp = client.post(f"/design/sessions/{sid}/follow-up", headers=headers)
    assert resp.status_code == 502


def test_finish_grades_and_updates_elo(client, db_session):
    _add_prompt(db_session, difficulty=900)
    headers = _auth_headers(client)
    sid = _create_session(client, headers)["session_id"]

    client.post(f"/design/sessions/{sid}/messages", headers=headers, json={"text": "My full design..."})

    before = client.get("/me", headers=headers).json()
    design_before = next(c for c in before["categories"] if c["category"] == "design")
    assert design_before["rating"] == 500

    with patch("app.design.router.grade_design_session", return_value=_fake_grade(overall=85)):
        resp = client.post(f"/design/sessions/{sid}/finish", headers=headers)

    assert resp.status_code == 200
    body = resp.json()
    assert body["overall_score"] == 0.85
    assert body["grade"]["overall"] == 85
    assert body["grade"]["improvements"] == [
        "Never addressed short-code collisions",
        "No story for the p99 target",
    ]
    assert body["grade"]["strengths"][0] == "Clear component breakdown"
    assert body["prompt_title"] == "URL Shortener"
    assert len(body["transcript"]) == 1
    assert body["rating_after"] > body["rating_before"]
    assert body["delta"] > 0
    assert "rubric_md" not in resp_text(body)
    assert "SECRET RUBRIC" not in resp_text(body)

    after = client.get("/me", headers=headers).json()
    design_after = next(c for c in after["categories"] if c["category"] == "design")
    assert design_after["sessions_count"] == 1
    assert design_after["rating"] == body["rating_after"]

    session = db_session.query(DesignSession).one()
    assert session.status == "graded"
    assert session.overall_score == 0.85
    assert session.elo_delta == body["delta"]
    assert session.graded_at is not None
    assert session.grade["overall"] == 85


def test_finish_with_empty_transcript_still_grades(client, db_session):
    _add_prompt(db_session)
    headers = _auth_headers(client)
    sid = _create_session(client, headers)["session_id"]

    with patch("app.design.router.grade_design_session", return_value=_fake_grade(overall=3)) as mock_grade:
        resp = client.post(f"/design/sessions/{sid}/finish", headers=headers)

    assert resp.status_code == 200
    assert resp.json()["overall_score"] == 0.03
    # grader was called with the (empty) transcript rather than erroring first
    assert mock_grade.call_args.args[3] == []


def test_finish_twice_is_409(client, db_session):
    _add_prompt(db_session)
    headers = _auth_headers(client)
    sid = _create_session(client, headers)["session_id"]

    with patch("app.design.router.grade_design_session", return_value=_fake_grade()):
        assert client.post(f"/design/sessions/{sid}/finish", headers=headers).status_code == 200
        resp = client.post(f"/design/sessions/{sid}/finish", headers=headers)
    assert resp.status_code == 409


def test_message_and_follow_up_rejected_after_grading(client, db_session):
    _add_prompt(db_session)
    headers = _auth_headers(client)
    sid = _create_session(client, headers)["session_id"]

    with patch("app.design.router.grade_design_session", return_value=_fake_grade()):
        client.post(f"/design/sessions/{sid}/finish", headers=headers)

    resp = client.post(f"/design/sessions/{sid}/messages", headers=headers, json={"text": "too late"})
    assert resp.status_code == 409
    resp = client.post(f"/design/sessions/{sid}/follow-up", headers=headers)
    assert resp.status_code == 409


def test_finish_returns_502_on_grading_failure(client, db_session):
    _add_prompt(db_session)
    headers = _auth_headers(client)
    sid = _create_session(client, headers)["session_id"]

    with patch("app.design.router.grade_design_session", side_effect=ValueError("boom")):
        resp = client.post(f"/design/sessions/{sid}/finish", headers=headers)
    assert resp.status_code == 502

    # session stays in_progress so the user can retry
    session = db_session.query(DesignSession).one()
    assert session.status == "in_progress"

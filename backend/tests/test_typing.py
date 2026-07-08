from app.models import TypingSnippet


def _auth_headers(client):
    resp = client.post(
        "/auth/signup",
        json={"email": "typist@example.com", "password": "hunter2222", "display_name": "Typist"},
    )
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def _add_snippet(db_session, content: str, difficulty: int = 1000) -> TypingSnippet:
    snippet = TypingSnippet(
        content=content,
        difficulty=difficulty,
        char_count=len(content),
        line_count=content.count("\n") + 1,
    )
    db_session.add(snippet)
    db_session.commit()
    db_session.refresh(snippet)
    return snippet


def test_queue_requires_auth(client):
    resp = client.get("/typing/queue", params={"mode": "classic"})
    assert resp.status_code == 401


def test_queue_without_snippets_returns_503(client):
    headers = _auth_headers(client)
    resp = client.get("/typing/queue", params={"mode": "classic"}, headers=headers)
    assert resp.status_code == 503


def test_queue_classic_returns_whole_snippets(client, db_session):
    _add_snippet(db_session, "x = 1\ny = 2")
    headers = _auth_headers(client)
    resp = client.get("/typing/queue", params={"mode": "classic"}, headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["mode"] == "classic"
    assert len(body["items"]) >= 60
    assert all(item["line_index"] is None for item in body["items"])
    assert all(item["content"] == "x = 1\ny = 2" for item in body["items"])


def test_queue_reaction_splits_into_non_blank_lines(client, db_session):
    _add_snippet(db_session, "x = 1\n\ny = 2")
    headers = _auth_headers(client)
    resp = client.get("/typing/queue", params={"mode": "reaction"}, headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    contents = {item["content"] for item in body["items"]}
    assert contents == {"x = 1", "y = 2"}
    assert all(item["line_index"] is not None for item in body["items"])


def test_submit_classic_attempt_scores_and_updates_elo(client, db_session):
    snippet = _add_snippet(db_session, "hello world", difficulty=500)
    headers = _auth_headers(client)

    resp = client.post(
        "/typing/attempts",
        headers=headers,
        json={
            "mode": "classic",
            "duration_s": 60,
            "elapsed_s": 60,
            "classic_items": [{"snippet_id": str(snippet.id), "typed": "hello world"}],
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["accuracy"] == 1.0
    assert body["rating_after"] != body["rating_before"] or body["delta"] == 0
    assert body["tier_after"]

    me = client.get("/me", headers=headers).json()
    typing_rating = next(c for c in me["categories"] if c["category"] == "typing")
    assert typing_rating["sessions_count"] == 1
    assert typing_rating["rating"] == body["rating_after"]


def test_submit_reaction_attempt_scores_and_updates_elo(client, db_session):
    snippet = _add_snippet(db_session, "return nums[i] + nums[j]", difficulty=1200)
    headers = _auth_headers(client)

    resp = client.post(
        "/typing/attempts",
        headers=headers,
        json={
            "mode": "reaction",
            "duration_s": 60,
            "elapsed_s": 30,
            "reaction_items": [
                {"snippet_id": str(snippet.id), "line_index": 0, "typed": "return arr[a] + arr[b]"}
            ],
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["lines_correct"] == 1
    assert body["lines_total"] == 1


def test_submit_infinite_classic_attempt_does_not_affect_elo(client, db_session):
    snippet = _add_snippet(db_session, "hello world", difficulty=500)
    headers = _auth_headers(client)

    before = client.get("/me", headers=headers).json()
    typing_before = next(c for c in before["categories"] if c["category"] == "typing")

    resp = client.post(
        "/typing/attempts",
        headers=headers,
        json={
            "mode": "classic",
            "duration_s": 0,
            "elapsed_s": 90,
            "classic_items": [{"snippet_id": str(snippet.id), "typed": "hello world"}],
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["accuracy"] == 1.0
    assert body["delta"] == 0
    assert body["rating_before"] == body["rating_after"] == typing_before["rating"]
    assert body["tier_before"] == body["tier_after"]

    after = client.get("/me", headers=headers).json()
    typing_after = next(c for c in after["categories"] if c["category"] == "typing")
    assert typing_after["rating"] == typing_before["rating"]
    assert typing_after["sessions_count"] == typing_before["sessions_count"]


def test_submit_reaction_attempt_flags_wrong_line(client, db_session):
    snippet = _add_snippet(db_session, "return len(nums)", difficulty=1200)
    headers = _auth_headers(client)

    resp = client.post(
        "/typing/attempts",
        headers=headers,
        json={
            "mode": "reaction",
            "duration_s": 60,
            "elapsed_s": 30,
            "reaction_items": [
                {"snippet_id": str(snippet.id), "line_index": 0, "typed": "return sum(nums)"}
            ],
        },
    )
    assert resp.status_code == 200
    assert resp.json()["lines_correct"] == 0


def test_submit_attempt_rejects_unknown_snippet_id(client, db_session):
    _add_snippet(db_session, "x = 1")
    headers = _auth_headers(client)
    resp = client.post(
        "/typing/attempts",
        headers=headers,
        json={
            "mode": "classic",
            "duration_s": 60,
            "elapsed_s": 30,
            "classic_items": [{"snippet_id": "00000000-0000-0000-0000-000000000000", "typed": "x = 1"}],
        },
    )
    assert resp.status_code == 400


def test_submit_attempt_rejects_invalid_line_index(client, db_session):
    snippet = _add_snippet(db_session, "x = 1")
    headers = _auth_headers(client)
    resp = client.post(
        "/typing/attempts",
        headers=headers,
        json={
            "mode": "reaction",
            "duration_s": 60,
            "elapsed_s": 30,
            "reaction_items": [{"snippet_id": str(snippet.id), "line_index": 5, "typed": "x = 1"}],
        },
    )
    assert resp.status_code == 400


def test_submit_classic_without_items_rejected(client, db_session):
    _add_snippet(db_session, "x = 1")
    headers = _auth_headers(client)
    resp = client.post(
        "/typing/attempts",
        headers=headers,
        json={"mode": "classic", "duration_s": 60, "elapsed_s": 30},
    )
    assert resp.status_code == 400


def test_submit_reaction_without_items_rejected(client, db_session):
    _add_snippet(db_session, "x = 1")
    headers = _auth_headers(client)
    resp = client.post(
        "/typing/attempts",
        headers=headers,
        json={"mode": "reaction", "duration_s": 60, "elapsed_s": 30},
    )
    assert resp.status_code == 400

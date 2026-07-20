from app.models import TypingSnippet


def _auth_headers(client):
    resp = client.post(
        "/auth/signup",
        json={"email": "stats@example.com", "password": "hunter2222", "display_name": "Stats Person"},
    )
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def _add_snippet(db_session, content: str, difficulty: int = 500) -> TypingSnippet:
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


def test_elo_history_requires_auth(client):
    resp = client.get("/stats/elo-history")
    assert resp.status_code == 401


def test_elo_history_empty_for_new_user(client):
    headers = _auth_headers(client)
    resp = client.get("/stats/elo-history", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["history"] == []


def test_elo_history_records_sessions_in_order(client, db_session):
    snippet = _add_snippet(db_session, "x = 1")
    headers = _auth_headers(client)

    for _ in range(3):
        client.post(
            "/typing/attempts",
            headers=headers,
            json={
                "mode": "classic",
                "duration_s": 60,
                "elapsed_s": 60,
                "classic_items": [{"snippet_id": str(snippet.id), "typed": "x = 1"}],
            },
        )

    resp = client.get("/stats/elo-history", headers=headers)
    assert resp.status_code == 200
    history = resp.json()["history"]
    assert len(history) == 3
    assert all(h["category"] == "typing" for h in history)
    assert all(h["source_type"] == "typing_attempt" for h in history)

    # ratings chain together: each entry's rating_before matches the previous rating_after
    for prev, cur in zip(history, history[1:]):
        assert cur["rating_before"] == prev["rating_after"]

    # ascending order by time
    timestamps = [h["created_at"] for h in history]
    assert timestamps == sorted(timestamps)


def test_summary_requires_auth(client):
    resp = client.get("/stats/summary")
    assert resp.status_code == 401


def test_summary_defaults_for_new_user(client):
    headers = _auth_headers(client)
    resp = client.get("/stats/summary", headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["overall_rating"] == 500
    assert body["overall_tier"] == "Intern"
    assert body["tier_floor"] == 300
    assert body["tier_next_floor"] == 600
    assert body["streak_days"] == 0
    assert len(body["categories"]) == 5
    for cat in body["categories"]:
        assert cat["rating"] == 500
        assert cat["best_rating"] == 500
        assert cat["sessions_count"] == 0
        assert cat["sessions_today"] == 0


def test_summary_reflects_sessions_played_today(client, db_session):
    snippet = _add_snippet(db_session, "x = 1")
    headers = _auth_headers(client)

    for _ in range(2):
        client.post(
            "/typing/attempts",
            headers=headers,
            json={
                "mode": "classic",
                "duration_s": 60,
                "elapsed_s": 60,
                "classic_items": [{"snippet_id": str(snippet.id), "typed": "x = 1"}],
            },
        )

    resp = client.get("/stats/summary", headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["streak_days"] == 1

    typing_summary = next(c for c in body["categories"] if c["category"] == "typing")
    assert typing_summary["sessions_count"] == 2
    assert typing_summary["sessions_today"] == 2
    # best_rating is a running max over every rating_after ever recorded, so it
    # can never be below the rating the user currently sits at.
    assert typing_summary["best_rating"] >= typing_summary["rating"]

    untouched = next(c for c in body["categories"] if c["category"] == "approach")
    assert untouched["sessions_today"] == 0
    assert untouched["best_rating"] == 500

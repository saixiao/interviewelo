def _signup(client, email="alice@example.com", password="hunter22!!", display_name="Alice"):
    return client.post(
        "/auth/signup",
        json={"email": email, "password": password, "display_name": display_name},
    )


def test_signup_creates_user_and_returns_access_token(client):
    resp = _signup(client)
    assert resp.status_code == 201
    body = resp.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]
    assert "refresh_token" in resp.cookies


def test_signup_rejects_duplicate_email(client):
    _signup(client)
    resp = _signup(client)
    assert resp.status_code == 409


def test_login_with_correct_password(client):
    _signup(client)
    resp = client.post("/auth/login", json={"email": "alice@example.com", "password": "hunter22!!"})
    assert resp.status_code == 200
    assert resp.json()["access_token"]


def test_login_with_wrong_password_rejected(client):
    _signup(client)
    resp = client.post("/auth/login", json={"email": "alice@example.com", "password": "wrong-password"})
    assert resp.status_code == 401


def test_me_requires_auth(client):
    resp = client.get("/me")
    assert resp.status_code == 401


def test_me_returns_starting_ratings_for_new_user(client):
    token = _signup(client).json()["access_token"]
    resp = client.get("/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["email"] == "alice@example.com"
    assert body["overall_rating"] == 500
    assert body["overall_tier"] == "Intern"
    assert len(body["categories"]) == 4
    assert all(c["rating"] == 500 and c["sessions_count"] == 0 for c in body["categories"])


def test_refresh_issues_new_access_token(client):
    _signup(client)
    resp = client.post("/auth/refresh")
    assert resp.status_code == 200
    assert resp.json()["access_token"]


def test_refresh_without_cookie_rejected(client):
    resp = client.post("/auth/refresh")
    assert resp.status_code == 401


def test_logout_clears_refresh_cookie(client):
    _signup(client)
    resp = client.post("/auth/logout")
    assert resp.status_code == 204

    refresh_resp = client.post("/auth/refresh")
    assert refresh_resp.status_code == 401

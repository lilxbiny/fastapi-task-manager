def test_register_user(client):
    resp = client.post(
        "/auth/register",
        json={"email": "alice@example.com", "password": "supersecret1"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["email"] == "alice@example.com"
    assert "id" in body
    assert "hashed_password" not in body  # never leak the hash


def test_register_duplicate_email_fails(client):
    payload = {"email": "bob@example.com", "password": "supersecret1"}
    first = client.post("/auth/register", json=payload)
    second = client.post("/auth/register", json=payload)
    assert first.status_code == 201
    assert second.status_code == 400


def test_login_success(client):
    client.post(
        "/auth/register",
        json={"email": "carol@example.com", "password": "supersecret1"},
    )
    resp = client.post(
        "/auth/login",
        data={"username": "carol@example.com", "password": "supersecret1"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"


def test_login_wrong_password_fails(client):
    client.post(
        "/auth/register",
        json={"email": "dave@example.com", "password": "supersecret1"},
    )
    resp = client.post(
        "/auth/login",
        data={"username": "dave@example.com", "password": "wrongpassword"},
    )
    assert resp.status_code == 401

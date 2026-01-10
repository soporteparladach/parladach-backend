from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app, raise_server_exceptions=False)


def test_me_without_token_returns_401():
    r = client.get("/auth/me")
    assert r.status_code == 401


def test_me_with_token_returns_200_and_user_data():
    email = "me_user@example.com"
    password = "Student123*"

    # crear usuario (si ya existe, aceptamos 200/409)
    r1 = client.post("/auth/register", json={"email": email, "password": password, "role": "STUDENT"})
    assert r1.status_code in (200, 409)

    login = client.post("/auth/login", json={"email": email, "password": password})
    assert login.status_code == 200
    token = login.json()["access_token"]

    me = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200

    data = me.json()
    assert data["email"] == email
    assert data["role"] == "STUDENT"
    assert data["status"] == "ACTIVE"
    assert "created_at" in data
    assert "password_hash" not in data

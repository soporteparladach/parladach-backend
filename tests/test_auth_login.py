from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app, raise_server_exceptions=False)


def test_login_valid_returns_token():
    # Debe existir un usuario ya creado (puedes crear uno vía /auth/register en el test o usar seed)
    # Recomendado: crear con register para no depender de seed.
    email = "login_ok@example.com"
    password = "Student123*"

    r1 = client.post("/auth/register", json={"email": email, "password": password, "role": "STUDENT"})
    assert r1.status_code in (200, 409)  # si ya existe, ok para este test

    r = client.post("/auth/login", json={"email": email, "password": password})
    assert r.status_code == 200
    data = r.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_returns_401_generic():
    r = client.post("/auth/login", json={"email": "noexiste@example.com", "password": "WrongPass123*"})
    assert r.status_code == 401
    # No filtrar información
    assert r.json()["error"]["message"] == "Credenciales inválidas"


def test_token_authenticates_protected_endpoint():
    email = "login_me@example.com"
    password = "Student123*"

    client.post("/auth/register", json={"email": email, "password": password, "role": "STUDENT"})

    login = client.post("/auth/login", json={"email": email, "password": password})
    assert login.status_code == 200
    token = login.json()["access_token"]

    me = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    data = me.json()
    assert data["email"] == email
    assert data["role"] == "STUDENT"

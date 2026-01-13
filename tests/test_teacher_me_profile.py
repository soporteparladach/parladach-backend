from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _register_and_login(email: str, password: str, role: str) -> str:
    client.post("/auth/register", json={"email": email, "password": password, "role": role})
    r = client.post("/auth/login", json={"email": email, "password": password})
    assert r.status_code == 200
    return r.json()["access_token"]


def test_teacher_get_profile_without_token_returns_401():
    r = client.get("/teacher/me/profile")
    assert r.status_code == 401


def test_student_cannot_access_teacher_profile_returns_403():
    token = _register_and_login("student_profile@test.com", "Student123*", "STUDENT")
    r = client.get("/teacher/me/profile", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 403


def test_teacher_can_create_and_get_profile():
    token = _register_and_login("teacher_profile@test.com", "Teacher123*", "TEACHER")

    # GET primero debe dar 404
    r1 = client.get("/teacher/me/profile", headers={"Authorization": f"Bearer {token}"})
    assert r1.status_code == 404

    # POST crea DRAFT (bio/languages opcional)
    r2 = client.post("/teacher/me/profile", json={}, headers={"Authorization": f"Bearer {token}"})
    assert r2.status_code == 200
    data = r2.json()["profile"]
    assert data["status"] == "DRAFT"
    assert data["bio"] == ""
    assert data["languages"] == []

    # GET ahora debe retornar el perfil
    r3 = client.get("/teacher/me/profile", headers={"Authorization": f"Bearer {token}"})
    assert r3.status_code == 200
    data2 = r3.json()["profile"]
    assert data2["id"] == data["id"]
    assert data2["status"] == "DRAFT"

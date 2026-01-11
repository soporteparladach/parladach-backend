from sqlalchemy import delete
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from app.main import app
from app.core.database import get_db
from app.models.user import User

client = TestClient(app)


def _cleanup_user(email: str) -> None:
    db: Session = next(get_db())
    db.execute(delete(User).where(User.email == email))
    db.commit()


def _register(email: str, password: str, role: str):
    return client.post("/auth/register", json={
        "email": email,
        "password": password,
        "role": role,
    })


def _login(email: str, password: str):
    return client.post("/auth/login", json={
        "email": email,
        "password": password,
    })


def test_register_student_ok():
    email = "min_register_student@test.com"
    password = "Student123*"
    _cleanup_user(email)

    r = _register(email, password, "STUDENT")
    assert r.status_code == 200
    data = r.json()

    # Validaciones mínimas (no expone password)
    assert "user" in data
    assert data["user"]["email"] == email
    assert data["user"]["role"] == "STUDENT"
    assert "password_hash" not in data["user"]


def test_login_ok_returns_token():
    email = "min_login_ok@test.com"
    password = "Student123*"
    _cleanup_user(email)

    r1 = _register(email, password, "STUDENT")
    assert r1.status_code == 200

    r2 = _login(email, password)
    assert r2.status_code == 200
    data = r2.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_auth_me_without_token_returns_401():
    r = client.get("/auth/me")
    assert r.status_code == 401


def test_dashboard_wrong_role_returns_403():
    # Crea STUDENT
    email = "min_wrong_role@test.com"
    password = "Student123*"
    _cleanup_user(email)

    r1 = _register(email, password, "STUDENT")
    assert r1.status_code == 200

    r2 = _login(email, password)
    assert r2.status_code == 200
    token = r2.json()["access_token"]

    # Intenta acceder a dashboard TEACHER con token STUDENT => 403
    r3 = client.get("/teacher/dashboard", headers={"Authorization": f"Bearer {token}"})
    assert r3.status_code == 403

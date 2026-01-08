from fastapi.testclient import TestClient
from sqlalchemy import text

from app.main import app
from app.core.database import engine

client = TestClient(app)


def _cleanup_user(email: str) -> None:
    # Limpieza directa para evitar dependencia de servicios/endpoint delete
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM users WHERE email = :email"), {"email": email})


def test_register_student_success():
    email = "student_reg_test@example.com"
    _cleanup_user(email)

    r = client.post("/auth/register", json={
        "email": email,
        "password": "Student123*",
        "role": "STUDENT",
    })
    assert r.status_code == 200
    data = r.json()
    assert data["user"]["email"] == email
    assert data["user"]["role"] == "STUDENT"
    assert data["user"]["status"] == "ACTIVE"
    assert "password_hash" not in data["user"]


def test_register_teacher_success():
    email = "teacher_reg_test@example.com"
    _cleanup_user(email)

    r = client.post("/auth/register", json={
        "email": email,
        "password": "Teacher123*",
        "role": "TEACHER",
    })
    assert r.status_code == 200
    data = r.json()
    assert data["user"]["email"] == email
    assert data["user"]["role"] == "TEACHER"


def test_register_duplicate_email_returns_409():
    email = "dup_reg_test@example.com"
    _cleanup_user(email)

    first = client.post("/auth/register", json={
        "email": email,
        "password": "Student123*",
        "role": "STUDENT",
    })
    assert first.status_code == 200

    second = client.post("/auth/register", json={
        "email": email,
        "password": "Student123*",
        "role": "STUDENT",
    })
    assert second.status_code == 409


def test_password_is_hashed_in_db():
    email = "hash_reg_test@example.com"
    _cleanup_user(email)

    r = client.post("/auth/register", json={
        "email": email,
        "password": "Student123*",
        "role": "STUDENT",
    })
    assert r.status_code == 200

    with engine.connect() as conn:
        row = conn.execute(
            text("SELECT password_hash FROM users WHERE email = :email"),
            {"email": email},
        ).fetchone()

    assert row is not None
    password_hash = row[0]
    assert password_hash is not None
    assert password_hash != "Student123*"
    assert "argon2" in password_hash.lower()

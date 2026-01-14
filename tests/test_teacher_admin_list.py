from __future__ import annotations

import os
from sqlalchemy.orm import Session
from sqlalchemy import select, delete
from fastapi.testclient import TestClient

from app.main import app
from app.core.database import get_db
from app.models.user import User
from app.core.enums import TeacherProfileStatus

client = TestClient(app)


def _cleanup_user(email: str) -> None:
    db: Session = next(get_db())
    db.execute(delete(User).where(User.email == email))
    db.commit()


def _register_user(email: str, password: str, role: str) -> None:
    client.post("/auth/register", json={"email": email, "password": password, "role": role})


def _login(email: str, password: str) -> str:
    r = client.post("/auth/login", json={"email": email, "password": password})
    assert r.status_code == 200, r.text
    return r.json()["access_token"]


def _login_admin_from_env_or_defaults() -> str:
    # Debe existir por scripts/create_admin.py (tarjeta 1.7)
    email = os.getenv("ADMIN_EMAIL", "admin@parladach.com")
    password = os.getenv("ADMIN_PASSWORD", "Admin123*")
    return _login(email, password)


def _set_profile_status(email: str, status: TeacherProfileStatus) -> None:
    from app.modules.teacher.models import TeacherProfile

    db: Session = next(get_db())
    user = db.execute(select(User).where(User.email == email)).scalar_one()
    profile = db.execute(select(TeacherProfile).where(TeacherProfile.user_id == user.id)).scalar_one()
    profile.status = status
    db.commit()


def test_admin_list_in_review_requires_admin_403_for_non_admin():
    email = "not_admin@test.com"
    _cleanup_user(email)

    _register_user(email, "Student123*", "STUDENT")
    token = _login(email, "Student123*")

    r = client.get("/admin/teachers?status=IN_REVIEW", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 403


def test_admin_can_list_in_review_profiles():
    teacher_email = "teacher_in_review@test.com"
    _cleanup_user(teacher_email)

    admin_token = _login_admin_from_env_or_defaults()

    _register_user(teacher_email, "Teacher123*", "TEACHER")
    teacher_token = _login(teacher_email, "Teacher123*")

    # crear perfil docente
    create = client.post("/teacher/me/profile", json={}, headers={"Authorization": f"Bearer {teacher_token}"})
    assert create.status_code == 200

    # ponerlo en IN_REVIEW
    _set_profile_status(teacher_email, TeacherProfileStatus.IN_REVIEW)

    r = client.get("/admin/teachers?status=IN_REVIEW", headers={"Authorization": f"Bearer {admin_token}"})
    assert r.status_code == 200
    data = r.json()
    assert "items" in data
    assert any(item["user_id"] == create.json()["profile"]["user_id"] for item in data["items"])

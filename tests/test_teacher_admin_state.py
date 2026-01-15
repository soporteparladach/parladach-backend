from __future__ import annotations

import os
from sqlalchemy.orm import Session
from sqlalchemy import select, delete
from fastapi.testclient import TestClient

from app.main import app
from app.core.database import get_db
from app.models.user import User
from app.core.enums import TeacherProfileStatus
from app.modules.teacher.models import TeacherProfile

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


def _login_admin() -> str:
    email = os.getenv("ADMIN_EMAIL", "admin@parladach.com")
    password = os.getenv("ADMIN_PASSWORD", "Admin123*")
    return _login(email, password)


def _set_profile_status_by_user(email: str, status: TeacherProfileStatus) -> int:
    db: Session = next(get_db())
    user = db.execute(select(User).where(User.email == email)).scalar_one()
    profile = db.execute(select(TeacherProfile).where(TeacherProfile.user_id == user.id)).scalar_one()
    profile.status = status
    db.commit()
    return profile.id


def test_admin_can_approve_in_review_profile():
    teacher_email = "teacher_to_approve@test.com"
    _cleanup_user(teacher_email)

    admin_token = _login_admin()

    _register_user(teacher_email, "Teacher123*", "TEACHER")
    teacher_token = _login(teacher_email, "Teacher123*")

    created = client.post("/teacher/me/profile", json={}, headers={"Authorization": f"Bearer {teacher_token}"})
    assert created.status_code == 200

    profile_id = _set_profile_status_by_user(teacher_email, TeacherProfileStatus.IN_REVIEW)

    r = client.post(
        f"/admin/teachers/{profile_id}/approve",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert r.status_code == 200
    assert r.json()["profile"]["status"] == "APPROVED"


def test_admin_can_pause_approved_profile():
    teacher_email = "teacher_to_pause@test.com"
    _cleanup_user(teacher_email)

    admin_token = _login_admin()

    _register_user(teacher_email, "Teacher123*", "TEACHER")
    teacher_token = _login(teacher_email, "Teacher123*")

    created = client.post("/teacher/me/profile", json={}, headers={"Authorization": f"Bearer {teacher_token}"})
    assert created.status_code == 200

    profile_id = _set_profile_status_by_user(teacher_email, TeacherProfileStatus.APPROVED)

    r = client.post(
        f"/admin/teachers/{profile_id}/pause",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert r.status_code == 200
    assert r.json()["profile"]["status"] == "PAUSED"


def test_invalid_transition_returns_400():
    teacher_email = "teacher_invalid_transition@test.com"
    _cleanup_user(teacher_email)

    admin_token = _login_admin()

    _register_user(teacher_email, "Teacher123*", "TEACHER")
    teacher_token = _login(teacher_email, "Teacher123*")

    created = client.post("/teacher/me/profile", json={}, headers={"Authorization": f"Bearer {teacher_token}"})
    assert created.status_code == 200

    profile_id = _set_profile_status_by_user(teacher_email, TeacherProfileStatus.DRAFT)

    # DRAFT -> APPROVED no permitido
    r = client.post(
        f"/admin/teachers/{profile_id}/approve",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert r.status_code == 400


def test_non_admin_gets_403():
    email = "not_admin_state@test.com"
    _cleanup_user(email)

    _register_user(email, "Student123*", "STUDENT")
    token = _login(email, "Student123*")

    r = client.post("/admin/teachers/1/approve", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 403

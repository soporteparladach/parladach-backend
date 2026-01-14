from sqlalchemy.orm import Session
from sqlalchemy import select, delete
from fastapi.testclient import TestClient

from app.main import app
from app.models.user import User
from app.core.database import get_db
from app.modules.teacher.models import TeacherProfile
from app.core.enums import TeacherProfileStatus

client = TestClient(app)


def _cleanup_user(email: str) -> None:
    db: Session = next(get_db())
    db.execute(delete(User).where(User.email == email))
    db.commit()


def _register_and_login(email: str, password: str, role: str) -> str:
    client.post("/auth/register", json={"email": email, "password": password, "role": role})
    r = client.post("/auth/login", json={"email": email, "password": password})
    assert r.status_code == 200
    return r.json()["access_token"]


def _set_profile_fields(email: str, *, bio: str, languages: list[str]) -> None:
    db: Session = next(get_db())
    user = db.execute(select(User).where(User.email == email)).scalar_one()
    profile = db.execute(select(TeacherProfile).where(TeacherProfile.user_id == user.id)).scalar_one()
    profile.bio = bio
    profile.languages = languages
    db.commit()


def _set_profile_status(email: str, status: TeacherProfileStatus) -> None:
    db: Session = next(get_db())
    user = db.execute(select(User).where(User.email == email)).scalar_one()
    profile = db.execute(select(TeacherProfile).where(TeacherProfile.user_id == user.id)).scalar_one()
    profile.status = status
    db.commit()


def test_submit_without_token_returns_401():
    r = client.post("/teacher/me/profile/submit")
    assert r.status_code == 401


def test_student_cannot_submit_returns_403():
    email = "student_submit@test.com"
    _cleanup_user(email)
    token = _register_and_login(email, "Student123*", "STUDENT")

    r = client.post("/teacher/me/profile/submit", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 403


def test_teacher_submit_requires_minimum_fields_returns_400():
    email = "teacher_submit_min@test.com"
    _cleanup_user(email)
    token = _register_and_login(email, "Teacher123*", "TEACHER")

    # crea perfil vacío
    created = client.post("/teacher/me/profile", json={}, headers={"Authorization": f"Bearer {token}"})
    assert created.status_code == 200
    assert created.json()["profile"]["status"] == "DRAFT"

    # submit debe fallar por mínimos
    r = client.post("/teacher/me/profile/submit", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 400


def test_teacher_submit_draft_to_in_review_success():
    email = "teacher_submit_ok@test.com"
    _cleanup_user(email)
    token = _register_and_login(email, "Teacher123*", "TEACHER")

    created = client.post("/teacher/me/profile", json={}, headers={"Authorization": f"Bearer {token}"})
    assert created.status_code == 200

    _set_profile_fields(email, bio="Bio lista", languages=["es"])

    r = client.post("/teacher/me/profile/submit", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    data = r.json()["profile"]
    assert data["status"] == "IN_REVIEW"


def test_teacher_submit_when_not_draft_returns_409():
    email = "teacher_submit_409@test.com"
    _cleanup_user(email)
    token = _register_and_login(email, "Teacher123*", "TEACHER")

    created = client.post("/teacher/me/profile", json={}, headers={"Authorization": f"Bearer {token}"})
    assert created.status_code == 200

    _set_profile_fields(email, bio="Bio lista", languages=["es"])
    _set_profile_status(email, TeacherProfileStatus.APPROVED)

    r = client.post("/teacher/me/profile/submit", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 409

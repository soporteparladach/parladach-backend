from sqlalchemy.orm import Session
from sqlalchemy import select, delete
from fastapi.testclient import TestClient

from app.main import app
from app.core.database import get_db
from app.models.user import User
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


def _set_profile_status(email: str, status: TeacherProfileStatus) -> int:
    db: Session = next(get_db())
    user = db.execute(select(User).where(User.email == email)).scalar_one()
    profile = db.execute(select(TeacherProfile).where(TeacherProfile.user_id == user.id)).scalar_one()
    profile.status = status
    db.commit()
    return profile.id


def test_public_teachers_returns_only_approved_without_auth():
    approved_email = "teacher_pub_ok@test.com"
    draft_email = "teacher_pub_draft@test.com"

    _cleanup_user(approved_email)
    _cleanup_user(draft_email)

    t1 = _register_and_login(approved_email, "Teacher123*", "TEACHER")
    t2 = _register_and_login(draft_email, "Teacher123*", "TEACHER")

    # crea perfiles
    r1 = client.post("/teacher/me/profile", json={"bio": "bio ok", "languages": ["es"]}, headers={"Authorization": f"Bearer {t1}"})
    assert r1.status_code == 200
    r2 = client.post("/teacher/me/profile", json={"bio": "bio draft", "languages": ["en"]}, headers={"Authorization": f"Bearer {t2}"})
    assert r2.status_code == 200

    approved_profile_id = _set_profile_status(approved_email, TeacherProfileStatus.APPROVED)
    _set_profile_status(draft_email, TeacherProfileStatus.DRAFT)

    # endpoint público sin token
    resp = client.get("/public/teachers")
    assert resp.status_code == 200

    data = resp.json()
    assert "items" in data

    ids = [it["teacher_profile_id"] for it in data["items"]]
    assert approved_profile_id in ids

    # draft NO debe aparecer
    draft_profile_id = r2.json()["profile"]["id"]
    assert draft_profile_id not in ids

    # no exponer campos sensibles
    for it in data["items"]:
        assert "email" not in it
        assert "user_id" not in it

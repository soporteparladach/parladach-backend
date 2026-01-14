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


def _set_teacher_profile_status(email: str, status: TeacherProfileStatus) -> None:
    db: Session = next(get_db())
    user = db.execute(select(User).where(User.email == email)).scalar_one()
    profile = db.execute(
        select(TeacherProfile).where(TeacherProfile.user_id == user.id)
    ).scalar_one()
    profile.status = status
    db.commit()


def _register_and_login(email: str, password: str, role: str) -> str:
    client.post("/auth/register", json={"email": email, "password": password, "role": role})
    r = client.post("/auth/login", json={"email": email, "password": password})
    assert r.status_code == 200
    return r.json()["access_token"]


def test_teacher_get_profile_without_token_returns_401():
    r = client.get("/teacher/me/profile")
    assert r.status_code == 401


def test_student_cannot_access_teacher_profile_returns_403():
    email = "student_profile@test.com"
    _cleanup_user(email)
    
    token = _register_and_login("student_profile@test.com", "Student123*", "STUDENT")
    r = client.get("/teacher/me/profile", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 403


def test_teacher_can_create_and_get_profile():
    email = "teacher_profile@test.com"
    _cleanup_user(email)

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
    assert data["created_at"] is not None
    assert data["updated_at"] is not None

    # GET ahora debe retornar el perfil
    r3 = client.get("/teacher/me/profile", headers={"Authorization": f"Bearer {token}"})
    assert r3.status_code == 200
    data2 = r3.json()["profile"]
    assert data2["id"] == data["id"]
    assert data2["status"] == "DRAFT"


def test_teacher_can_patch_profile_in_draft():
    email = "teacher_patch_draft@test.com"
    _cleanup_user(email)

    token = _register_and_login(email, "Teacher123*", "TEACHER")
    create = client.post("/teacher/me/profile", json={}, headers={"Authorization": f"Bearer {token}"})
    assert create.status_code == 200
    before = create.json()["profile"]["updated_at"]

    r = client.patch(
        "/teacher/me/profile",
        json={"bio": "Hola, soy docente", "languages": ["es", "en"], "photo_url": "https://img.test/p.png"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    data = r.json()["profile"]
    assert data["status"] == "DRAFT"
    assert data["bio"] == "Hola, soy docente"
    assert data["languages"] == ["es", "en"]
    assert data["photo_url"] == "https://img.test/p.png"
    assert data["updated_at"] != before


def test_teacher_cannot_patch_profile_in_review_returns_409():
    email = "teacher_patch_review@test.com"
    _cleanup_user(email)

    token = _register_and_login(email, "Teacher123*", "TEACHER")
    created = client.post("/teacher/me/profile", json={}, headers={"Authorization": f"Bearer {token}"})
    assert created.status_code == 200

    _set_teacher_profile_status(email, TeacherProfileStatus.IN_REVIEW)

    r = client.patch(
        "/teacher/me/profile",
        json={"bio": "cambio"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 409


def test_teacher_patch_on_approved_sets_in_review_when_key_fields_change():
    email = "teacher_patch_approved@test.com"
    _cleanup_user(email)

    token = _register_and_login(email, "Teacher123*", "TEACHER")
    created = client.post("/teacher/me/profile", json={}, headers={"Authorization": f"Bearer {token}"})
    assert created.status_code == 200

    _set_teacher_profile_status(email, TeacherProfileStatus.APPROVED)

    r = client.patch(
        "/teacher/me/profile",
        json={"bio": "nuevo bio"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    data = r.json()["profile"]
    assert data["status"] == "IN_REVIEW"


    
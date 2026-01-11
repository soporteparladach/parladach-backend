from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.core.database import get_db
from app.core.security import hash_password
from app.core.enums import UserRole, UserStatus
from app.models.user import User

client = TestClient(app)


def _register_and_login(email: str, password: str, role: str) -> str:
    r = client.post("/auth/register", json={"email": email, "password": password, "role": role})
    assert r.status_code in (200, 409)

    login = client.post("/auth/login", json={"email": email, "password": password})
    assert login.status_code == 200
    return login.json()["access_token"]


def _create_admin_and_login(email: str, password: str) -> str:
    db: Session = next(get_db())
    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(
            email=email,
            password_hash=hash_password(password),
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE,
        )
        db.add(user)
        db.commit()

    login = client.post("/auth/login", json={"email": email, "password": password})
    assert login.status_code == 200
    return login.json()["access_token"]


def test_student_dashboard_requires_token():
    r = client.get("/student/dashboard")
    assert r.status_code == 401


def test_teacher_dashboard_requires_token():
    r = client.get("/teacher/dashboard")
    assert r.status_code == 401


def test_admin_dashboard_requires_token():
    r = client.get("/admin/dashboard")
    assert r.status_code == 401


def test_student_dashboard_forbidden_for_teacher():
    token = _register_and_login("t_for_student@test.com", "Teacher123*", "TEACHER")
    r = client.get("/student/dashboard", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 403


def test_teacher_dashboard_forbidden_for_student():
    token = _register_and_login("s_for_teacher@test.com", "Student123*", "STUDENT")
    r = client.get("/teacher/dashboard", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 403


def test_admin_dashboard_forbidden_for_student():
    token = _register_and_login("s_for_admin@test.com", "Student123*", "STUDENT")
    r = client.get("/admin/dashboard", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 403


def test_student_dashboard_allowed_for_student():
    token = _register_and_login("student_dash@test.com", "Student123*", "STUDENT")
    r = client.get("/student/dashboard", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    data = r.json()
    assert data["role"] == "STUDENT"
    assert "user_id" in data


def test_teacher_dashboard_allowed_for_teacher():
    token = _register_and_login("teacher_dash@test.com", "Teacher123*", "TEACHER")
    r = client.get("/teacher/dashboard", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    data = r.json()
    assert data["role"] == "TEACHER"
    assert "user_id" in data


def test_admin_dashboard_allowed_for_admin():
    token = _create_admin_and_login("admin_dash@test.com", "Admin123*")
    r = client.get("/admin/dashboard", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    data = r.json()
    assert data["role"] == "ADMIN"
    assert "user_id" in data

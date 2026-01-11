from sqlalchemy.orm import Session
from sqlalchemy import select, delete
from fastapi.testclient import TestClient

from app.main import app
from app.core.database import get_db
from app.core.enums import UserStatus
from app.models.user import User

client = TestClient(app)


def _cleanup_user(email: str) -> None:
    db: Session = next(get_db())
    db.execute(delete(User).where(User.email == email))
    db.commit()


def _register_and_login(email: str, password: str, role: str) -> str:
    client.post("/auth/register", json={"email": email, "password": password, "role": role})
    login = client.post("/auth/login", json={"email": email, "password": password})
    assert login.status_code == 200
    return login.json()["access_token"]


def _set_status(email: str, status: UserStatus) -> None:
    db: Session = next(get_db())
    user = db.execute(select(User).where(User.email == email)).scalar_one()
    user.status = status
    db.commit()


def test_suspended_user_cannot_access_me_returns_403():
    email = "susp@test.com"

    _cleanup_user(email)
    
    token = _register_and_login(email, "Student123*", "STUDENT")
    _set_status(email, UserStatus.SUSPENDED)

    r = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 403


def test_deleted_user_cannot_access_dashboard_returns_403():
    email = "del@test.com"

    _cleanup_user(email)
    
    token = _register_and_login(email, "Student123*", "STUDENT")
    _set_status(email, UserStatus.DELETED)

    r = client.get("/student/dashboard", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 403


def test_suspended_user_login_returns_401_generic():
    email = "susp_login@test.com"
    password = "Student123*"

    _cleanup_user(email)

    client.post("/auth/register", json={"email": email, "password": password, "role": "STUDENT"})
    _set_status(email, UserStatus.SUSPENDED)

    r = client.post("/auth/login", json={"email": email, "password": password})
    assert r.status_code == 401
    assert r.json()["error"]["message"] == "Credenciales inválidas"


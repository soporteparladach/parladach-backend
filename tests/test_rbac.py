from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.core.database import get_db
from app.core.security import hash_password
from app.models.user import User
from app.core.enums import UserRole, UserStatus

client = TestClient(app)


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

    login = client.post("/auth/login", json={
        "email": email,
        "password": password,
    })

    assert login.status_code == 200
    return login.json()["access_token"]


def test_rbac_admin_endpoint_allowed_for_admin():
    token = _create_admin_and_login(
        email="admin_rbac@test.com",
        password="Admin123*",
    )

    r = client.get(
        "/auth/me/admin-test",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert r.status_code == 200

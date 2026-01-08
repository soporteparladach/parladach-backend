from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session
from starlette.status import HTTP_400_BAD_REQUEST

from app.core.enums import UserRole, UserStatus
from app.core.errors import AppError, ConflictError
from app.core.security import hash_password
from app.models.user import User


class AuthService:
    def register(self, db: Session, *, email: str, password: str, role: UserRole) -> User:
        # Regla: rol permitido al registrarse
        if role not in {UserRole.STUDENT, UserRole.TEACHER}:
            raise AppError("Rol no permitido para registro", status_code=HTTP_400_BAD_REQUEST)

        # Email único
        exists = db.execute(select(User).where(User.email == email)).scalar_one_or_none()
        if exists:
            raise ConflictError("Email ya registrado")

        user = User(
            email=email,
            password_hash=hash_password(password),
            role=role,
            status=UserStatus.ACTIVE,
        )

        db.add(user)
        db.commit()
        db.refresh(user)
        return user

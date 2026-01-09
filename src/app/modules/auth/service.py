from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session
from starlette.status import HTTP_400_BAD_REQUEST
from fastapi import HTTPException, status

from app.core.enums import UserRole, UserStatus
from app.core.errors import AppError, ConflictError
from app.core.security import hash_password
from app.models.user import User
from app.modules.auth.security import verify_password, create_access_token


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


    def login(self, db: Session, *, email: str, password: str) -> str:
        user = db.execute(select(User).where(User.email == email)).scalar_one_or_none()

        # Respuesta genérica: no filtrar si existe o no
        if not user or not getattr(user, "password_hash", None) or not verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales inválidas",
            )
        
        token = create_access_token(
            sub=str(user.id),
            role=str(user.role.value if hasattr(user.role, "value") else user.role),
            status=str(user.status.value if hasattr(user.status, "value") else user.status),
        )
        return token
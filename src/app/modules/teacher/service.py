from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import User
from app.core.enums import UserRole


class TeacherService:
    def assert_user_is_teacher(self, db: Session, *, user_id: int) -> None:
        user = db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
        if not user or user.role != UserRole.TEACHER:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Solo usuarios con rol TEACHER pueden tener perfil docente",
            )

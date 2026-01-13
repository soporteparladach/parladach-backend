from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import User
from app.core.enums import UserRole
from app.core.enums import TeacherProfileStatus
from app.modules.teacher.models import TeacherProfile


class TeacherService:
    def assert_user_is_teacher(self, db: Session, *, user_id: int) -> None:
        user = db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
        if not user or user.role != UserRole.TEACHER:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Solo usuarios con rol TEACHER pueden tener perfil docente",
            )
        
    def get_profile_by_user_id(self, db: Session, *, user_id: int) -> TeacherProfile | None:
        return db.execute(
            select(TeacherProfile).where(TeacherProfile.user_id == user_id)
        ).scalar_one_or_none()

    def create_profile_if_not_exists(
        self,
        db: Session,
        *,
        user_id: int,
        bio: str | None,
        languages: list[str] | None,
        photo_url: str | None,
    ) -> TeacherProfile:
        existing = self.get_profile_by_user_id(db, user_id=user_id)
        if existing:
            return existing

        profile = TeacherProfile(
            user_id=user_id,
            bio=bio or "",
            languages=languages or [],
            photo_url=photo_url,
            status=TeacherProfileStatus.DRAFT,
        )

        db.add(profile)
        db.commit()
        db.refresh(profile)
        return profile

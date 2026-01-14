from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import User
from app.core.enums import UserRole, TeacherProfileStatus
from app.modules.teacher.models import TeacherProfile
from app.modules.teacher.schemas import TeacherProfileUpdate


KEY_FIELDS = {"bio", "languages", "photo_url"}


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


    def update_my_profile(self, db: Session, *, user_id: int, payload: TeacherProfileUpdate) -> TeacherProfile:
        profile = db.execute(
            select(TeacherProfile).where(TeacherProfile.user_id == user_id)
        ).scalar_one_or_none()

        if not profile:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Perfil docente no existe")

        # Reglas por estado
        if profile.status == TeacherProfileStatus.IN_REVIEW:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El perfil está en revisión y no se puede editar",
            )

        data = payload.model_dump(exclude_unset=True)

        # Determinar si cambian campos clave
        key_changed = any(k in data for k in KEY_FIELDS)

        # Aplicar cambios
        for k, v in data.items():
            setattr(profile, k, v)

        # Si estaba APPROVED y cambia algo clave => IN_REVIEW
        if profile.status == TeacherProfileStatus.APPROVED and key_changed:
            profile.status = TeacherProfileStatus.IN_REVIEW

        db.add(profile)
        db.commit()
        db.refresh(profile)
        return profile
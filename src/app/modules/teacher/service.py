from __future__ import annotations

from sqlalchemy import select, func, desc
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import User
from app.core.enums import UserRole, TeacherProfileStatus
from app.modules.teacher.models import TeacherProfile
from app.modules.teacher.schemas import TeacherProfileUpdate
from app.modules.teacher.schemas import TeacherProfilePublic


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
    
    def submit_my_profile(self, db: Session, *, user_id: int) -> TeacherProfile:
        profile = self.get_profile_by_user_id(db, user_id=user_id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Perfil docente no existe",
            )

        if profile.status != TeacherProfileStatus.DRAFT:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Solo puedes enviar a revisión un perfil en estado DRAFT",
            )

        bio_ok = bool((profile.bio or "").strip())
        languages_ok = bool(profile.languages) and len(profile.languages) > 0

        if not bio_ok or not languages_ok:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Para enviar a revisión, completa bio y languages",
            )

        profile.status = TeacherProfileStatus.IN_REVIEW

        db.add(profile)
        db.commit()
        db.refresh(profile)
        return profile
    

    def admin_list_profiles(
        self,
        db: Session,
        *,
        status: str | None,
        limit: int,
        offset: int,
    ) -> tuple[list[TeacherProfilePublic], int]:
        q = select(TeacherProfile)
        cq = select(func.count()).select_from(TeacherProfile)

        if status:
            # Validar/normalizar status contra enum
            try:
                enum_status = TeacherProfileStatus(status)
            except ValueError:
                # si prefieres 400, cámbialo a HTTPException(400,...)
                enum_status = None

            if enum_status:
                q = q.where(TeacherProfile.status == enum_status)
                cq = cq.where(TeacherProfile.status == enum_status)

        total = db.execute(cq).scalar_one()
        rows = db.execute(q.order_by(TeacherProfile.id).limit(limit).offset(offset)).scalars().all()

        # Convertir a esquema público
        items = [TeacherProfilePublic.model_validate(p) for p in rows]
        return items, total
    

    def admin_set_status(self, db: Session, *, profile_id: int, action: str) -> TeacherProfile:
        profile = db.execute(
            select(TeacherProfile).where(TeacherProfile.id == profile_id)
        ).scalar_one_or_none()

        if not profile:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Perfil docente no existe")

        current = profile.status

        if action == "approve":
            # IN_REVIEW -> APPROVED, PAUSED -> APPROVED
            if current not in {TeacherProfileStatus.IN_REVIEW, TeacherProfileStatus.PAUSED}:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Transición inválida: {current} -> APPROVED",
                )
            profile.status = TeacherProfileStatus.APPROVED

        elif action == "pause":
            # APPROVED -> PAUSED
            if current != TeacherProfileStatus.APPROVED:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Transición inválida: {current} -> PAUSED",
                )
            profile.status = TeacherProfileStatus.PAUSED

        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Acción inválida")

        db.add(profile)
        db.commit()
        db.refresh(profile)
        return profile
    

    def list_public_approved_profiles(
        self,
        db: Session,
        *,
        limit: int = 50,
        offset: int = 0,
    ) -> list[TeacherProfile]:
        stmt = (
            select(TeacherProfile)
            .where(TeacherProfile.status == TeacherProfileStatus.APPROVED)
            .order_by(desc(TeacherProfile.created_at), desc(TeacherProfile.id))
            .limit(limit)
            .offset(offset)
        )
        return list(db.execute(stmt).scalars().all())
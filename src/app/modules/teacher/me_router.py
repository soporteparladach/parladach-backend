from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.modules.teacher.dependencies import require_teacher
from app.modules.teacher.schemas import (
    TeacherProfileCreate,
    TeacherProfilePublic,
    TeacherProfileResponse,
)
from app.modules.teacher.service import TeacherService

router = APIRouter(prefix="/teacher", tags=["teacher-me"])


@router.get("/me/profile", response_model=TeacherProfileResponse, operation_id="teacher_get_my_profile")
def get_my_profile(
    user: User = Depends(require_teacher),
    db: Session = Depends(get_db),
) -> TeacherProfileResponse:
    service = TeacherService()
    profile = service.get_profile_by_user_id(db, user_id=user.id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Perfil docente no existe")

    return TeacherProfileResponse(
        profile=TeacherProfilePublic(
            id=profile.id,
            user_id=profile.user_id,
            bio=profile.bio,
            languages=profile.languages,
            photo_url=profile.photo_url,
            status=profile.status,
            created_at=profile.created_at,
            updated_at=profile.updated_at,
        )
    )


@router.post("/me/profile", response_model=TeacherProfileResponse, operation_id="teacher_create_my_profile")
def create_my_profile(
    payload: TeacherProfileCreate,
    user: User = Depends(require_teacher),
    db: Session = Depends(get_db),
) -> TeacherProfileResponse:
    service = TeacherService()
    profile = service.create_profile_if_not_exists(
        db,
        user_id=user.id,
        bio=payload.bio,
        languages=payload.languages,
        photo_url=payload.photo_url,
    )

    return TeacherProfileResponse(
        profile=TeacherProfilePublic(
            id=profile.id,
            user_id=profile.user_id,
            bio=profile.bio,
            languages=profile.languages,
            photo_url=profile.photo_url,
            status=profile.status,
            created_at=profile.created_at,
            updated_at=profile.updated_at,
        )
    )

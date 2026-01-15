from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.modules.auth.dependencies import require_roles
from app.modules.teacher.schemas import TeacherProfileListResponse
from app.modules.teacher.service import TeacherService
from app.modules.teacher.schemas import TeacherProfileResponse


router = APIRouter(
    prefix="/admin/teachers",
    tags=["admin-teachers"],
)

@router.get("", response_model=TeacherProfileListResponse, operation_id="admin_list_teacher_profiles")
def list_teacher_profiles(
    status: str | None = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("ADMIN")),
) -> TeacherProfileListResponse:
    items, total = TeacherService().admin_list_profiles(db, status=status, limit=limit, offset=offset)
    return TeacherProfileListResponse(items=items, total=total, limit=limit, offset=offset)


@router.post(
    "/{teacher_profile_id}/approve",
    response_model=TeacherProfileResponse,
    operation_id="admin_approve_teacher_profile",
)
def approve_teacher_profile(
    teacher_profile_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("ADMIN")),
) -> TeacherProfileResponse:
    profile = TeacherService().admin_set_status(db, profile_id=teacher_profile_id, action="approve")
    return TeacherProfileResponse.from_orm_profile(profile)


@router.post(
    "/{teacher_profile_id}/pause",
    response_model=TeacherProfileResponse,
    operation_id="admin_pause_teacher_profile",
)
def pause_teacher_profile(
    teacher_profile_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("ADMIN")),
) -> TeacherProfileResponse:
    profile = TeacherService().admin_set_status(db, profile_id=teacher_profile_id, action="pause")
    return TeacherProfileResponse.from_orm_profile(profile)
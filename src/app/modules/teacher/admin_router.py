from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.modules.auth.dependencies import require_roles
from app.modules.teacher.schemas import TeacherProfileListResponse
from app.modules.teacher.service import TeacherService


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
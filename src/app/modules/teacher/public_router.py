from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.teacher.service import TeacherService
from app.modules.teacher.schemas import PublicTeachersResponse, PublicTeacherItem

router = APIRouter(prefix="/public", tags=["public-teachers"])


@router.get("/teachers", response_model=PublicTeachersResponse, operation_id="public_teachers_list")
def public_teachers_list(
    db: Session = Depends(get_db),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> PublicTeachersResponse:
    profiles = TeacherService().list_public_approved_profiles(db, limit=limit, offset=offset)

    items = [
        PublicTeacherItem(
            teacher_profile_id=p.id,
            bio=p.bio,
            languages=p.languages,
            photo_url=p.photo_url,
            display_name=None,  # si luego hay display_name en User, se completa aquí
        )
        for p in profiles
    ]

    return PublicTeachersResponse(items=items)

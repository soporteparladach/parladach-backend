from fastapi import APIRouter, Depends

from app.models.user import User
from app.modules.auth.dependencies import require_roles

router = APIRouter(tags=["dashboard"])


def _role_value(user: User) -> str:
    return user.role.value if hasattr(user.role, "value") else str(user.role)


@router.get("/student/dashboard", operation_id="student_dashboard")
def student_dashboard(user: User = Depends(require_roles("STUDENT"))) -> dict:
    return {
        "message": "Dashboard estudiante",
        "user_id": user.id,
        "role": _role_value(user),
    }


@router.get("/teacher/dashboard", operation_id="teacher_dashboard")
def teacher_dashboard(user: User = Depends(require_roles("TEACHER"))) -> dict:
    return {
        "message": "Dashboard docente",
        "user_id": user.id,
        "role": _role_value(user),
    }


@router.get("/admin/dashboard", operation_id="admin_dashboard")
def admin_dashboard(user: User = Depends(require_roles("ADMIN"))) -> dict:
    return {
        "message": "Dashboard administrador",
        "user_id": user.id,
        "role": _role_value(user),
    }

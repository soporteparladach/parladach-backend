from __future__ import annotations

from fastapi import Depends

from app.models.user import User
from app.modules.auth.dependencies import require_roles


def require_teacher(user: User = Depends(require_roles("TEACHER"))) -> User:
    return user

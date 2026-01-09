from __future__ import annotations

import jwt
from jwt import InvalidTokenError
from typing import Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config.settings import settings
from app.core.database import get_db
from app.models.user import User

bearer_scheme = HTTPBearer(auto_error=False)


def _unauthorized() -> HTTPException:
    return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No autenticado")


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise _unauthorized()

    token = credentials.credentials
    algorithm = settings.JWT_ALGORITHM 

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[algorithm])
    except InvalidTokenError:
        raise _unauthorized()

    sub = payload.get("sub")
    if not sub:
        raise _unauthorized()
    
    try:
        user_id = int(sub)
    except (TypeError, ValueError):
        raise _unauthorized()

    user = db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
    if not user:
        raise _unauthorized()

    return user


def require_role(*roles: str) -> Callable:
    def dependency(user: User = Depends(get_current_user)) -> User:
        user_role = user.role.value if hasattr(user.role, "value") else str(user.role)
        if user_role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado")
        return user

    return dependency

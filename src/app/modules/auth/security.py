from __future__ import annotations

from datetime import datetime, timedelta, timezone
import jwt

from app.config.settings import settings
from app.core.security import password_hasher  # el objeto de pwdlib
# Si no exportaste password_hasher, ver sección 3.1 abajo.


def verify_password(password: str, password_hash: str) -> bool:
    return password_hasher.verify(password, password_hash)


def create_access_token(*, sub: str, role: str, status: str) -> str:
    expires_minutes = settings.ACCESS_TOKEN_EXPIRES_MINUTES
    algorithm = settings.JWT_ALGORITHM

    now = datetime.now(timezone.utc)
    exp = now + timedelta(minutes=expires_minutes)

    payload = {
        "sub": sub,
        "role": role,
        "status": status,
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
    }

    return jwt.encode(payload, settings.SECRET_KEY, algorithm=algorithm)

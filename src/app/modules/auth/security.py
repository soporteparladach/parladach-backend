"""
Utilidades de seguridad del módulo auth.

En TARJETA 1.1 solo se define estructura.
La implementación concreta (argon2, jwt, refresh tokens) se completa en tarjetas posteriores.
"""
from __future__ import annotations

from app.core.security import hash_password  # reutiliza hashing global existente


def verify_password(_: str, __: str) -> bool:
    # Placeholder: se implementa en tarjeta de login
    return False


def create_access_token(_: dict) -> str:
    # Placeholder: se implementa con JWT en tarjeta posterior
    return ""

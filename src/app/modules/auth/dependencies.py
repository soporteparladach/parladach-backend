"""
Dependencias del módulo auth.

Se completan en tarjetas de autenticación/autorización:
- get_current_user (auth required)
- require_role (role required)
"""
from __future__ import annotations

from typing import Callable

from fastapi import Depends, HTTPException, status


def get_current_user():
    """
    Placeholder de dependencia 'auth required'.
    Se implementa cuando existan tokens.
    """
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No autenticado",
    )


def require_role(*roles: str) -> Callable:
    """
    Placeholder de dependencia 'role required'.
    Se implementa cuando exista current_user real.
    """
    def dependency(_=Depends(get_current_user)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No autorizado",
        )

    return dependency

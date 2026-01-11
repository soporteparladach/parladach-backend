from __future__ import annotations

import os
import sys
from pathlib import Path

# Permite ejecutar el script desde /backend sin instalar el paquete
sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.core.enums import UserRole, UserStatus
from app.models.user import User


def _get_env(name: str) -> str:
    value = os.getenv(name)
    if not value or not value.strip():
        raise RuntimeError(f"Falta variable de entorno requerida: {name}")
    return value.strip()


def main() -> None:
    email = _get_env("ADMIN_EMAIL").lower()
    password = _get_env("ADMIN_PASSWORD")

    db: Session = SessionLocal()
    try:
        existing = db.execute(select(User).where(User.email == email)).scalar_one_or_none()

        if existing:
            # Si ya existe, solo asegura rol/status correctos
            changed = False
            if existing.role != UserRole.ADMIN:
                existing.role = UserRole.ADMIN
                changed = True
            if existing.status != UserStatus.ACTIVE:
                existing.status = UserStatus.ACTIVE
                changed = True

            if changed:
                db.commit()

            print(f"ADMIN ya existe: {email}")
            return

        admin = User(
            email=email,
            password_hash=hash_password(password),
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE,
        )

        db.add(admin)
        db.commit()
        print(f"ADMIN creado: {email}")

    finally:
        db.close()


if __name__ == "__main__":
    main()

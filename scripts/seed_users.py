import sys
from pathlib import Path

# Permite ejecutar el script desde /backend sin instalar paquete adicional
sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from sqlalchemy import select  # noqa: E402

from app.core.database import SessionLocal  # noqa: E402
from app.core.enums import UserRole, UserStatus  # noqa: E402
from app.core.security import hash_password  # noqa: E402
from app.models.user import User  # noqa: E402


SEED_USERS = [
    {
        "email": "admin@parladach.local",
        "password": "Admin123*",
        "role": UserRole.ADMIN,
    },
    {
        "email": "student@parladach.local",
        "password": "Student123*",
        "role": UserRole.STUDENT,
    },
    {
        "email": "teacher@parladach.local",
        "password": "Teacher123*",
        "role": UserRole.TEACHER,
    },
]


def main() -> None:
    db = SessionLocal()
    try:
        created = 0
        for u in SEED_USERS:
            exists = db.execute(select(User).where(User.email == u["email"])).scalar_one_or_none()
            if exists:
                continue

            user = User(
                email=u["email"],
                password_hash=hash_password(u["password"]),
                role=u["role"],
                status=UserStatus.ACTIVE,
            )
            db.add(user)
            created += 1

        db.commit()
        print(f"Seed completado. Usuarios creados: {created}.")
    finally:
        db.close()


if __name__ == "__main__":
    main()

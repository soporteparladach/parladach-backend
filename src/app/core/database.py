from __future__ import annotations

from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config.settings import settings


# Engine: configura conexión (NO crea tablas)
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,  # evita conexiones muertas
)


# Session factory (SQLAlchemy 2.0 style)
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency para FastAPI:
    - abre sesión
    - entrega sesión
    - cierra sesión correctamente
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

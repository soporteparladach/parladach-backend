from fastapi import APIRouter
from app.config.settings import settings

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check() -> dict:
    return {"status": "ok", "env": settings.app_env}

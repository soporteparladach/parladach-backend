from fastapi import FastAPI

from app.config.settings import settings
from app.api.routes.health import router as health_router


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name)
    app.include_router(health_router)
    return app


app = create_app()

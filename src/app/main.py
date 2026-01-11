from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.routes.health import router as health_router
from app.config.settings import settings
from app.core.logging import configure_logging
from app.core.middlewares import request_logging_middleware
from app.core.errors import (
    AppError,
    app_error_handler,
    validation_error_handler,
    internal_error_handler,
    http_exception_handler
)
from app.modules.auth.router import router as auth_router
from app.modules.dashboard.router import router as dashboard_router

def create_app() -> FastAPI:
    configure_logging(settings.app_env)

    app = FastAPI(title=settings.app_name)

    # Middleware de logging por request
    app.middleware("http")(request_logging_middleware)

    # Exception handlers (respuestas consistentes)
    app.add_exception_handler(AppError, app_error_handler)    
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)
    app.add_exception_handler(Exception, internal_error_handler)

    app.include_router(health_router)
    app.include_router(auth_router)
    app.include_router(dashboard_router)

    return app


app = create_app()

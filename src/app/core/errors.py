from __future__ import annotations

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_422_UNPROCESSABLE_CONTENT,
    HTTP_500_INTERNAL_SERVER_ERROR,
)


class AppError(Exception):
    """Excepción base del dominio/aplicación."""
    status_code: int = HTTP_400_BAD_REQUEST

    def __init__(self, message: str, *, status_code: int | None = None) -> None:
        super().__init__(message)
        if status_code is not None:
            self.status_code = status_code


async def app_error_handler(_: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"type": exc.__class__.__name__, "message": str(exc)}},
    )


async def not_found_handler(_: Request, __) -> JSONResponse:
    return JSONResponse(
        status_code=HTTP_404_NOT_FOUND,
        content={"error": {"type": "NotFound", "message": "Recurso no encontrado"}},
    )


async def validation_error_handler(_: Request, exc) -> JSONResponse:
    # FastAPI / Pydantic validation errors
    return JSONResponse(
        status_code=HTTP_422_UNPROCESSABLE_CONTENT,
        content={"error": {"type": "ValidationError", "message": "Datos inválidos", "details": exc.errors()}},
    )


async def internal_error_handler(_: Request, __) -> JSONResponse:
    return JSONResponse(
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": {"type": "InternalServerError", "message": "Error interno"}},
    )

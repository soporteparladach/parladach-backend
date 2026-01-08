from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.auth.schemas import RegisterRequest, RegisterResponse, UserPublic
from app.modules.auth.service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/health", operation_id="auth_health")
def auth_health() -> dict:
    return {"status": "ok"}


@router.post("/register", response_model=RegisterResponse, operation_id="auth_register")
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> RegisterResponse:
    service = AuthService()
    user = service.register(db, email=payload.email, password=payload.password, role=payload.role)

    return RegisterResponse(
        user=UserPublic(
            id=user.id,
            email=user.email,
            role=user.role,
            status=user.status,
        )
    )

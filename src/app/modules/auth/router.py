from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.auth.schemas import RegisterRequest, RegisterResponse, UserPublic
from app.modules.auth.service import AuthService
from app.models.user import User
from app.modules.auth.schemas import LoginRequest, TokenResponse, UserPublic
from app.modules.auth.dependencies import get_current_user


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


@router.post("/login", response_model=TokenResponse, operation_id="auth_login")
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    token = AuthService().login(db, email=payload.email, password=payload.password)
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserPublic, operation_id="auth_me")
def me(user: User = Depends(get_current_user)) -> UserPublic:
    return UserPublic(
        id=user.id,
        email=user.email,
        role=user.role,
        status=user.status,
    )
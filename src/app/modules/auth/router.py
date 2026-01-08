from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["auth"])

@router.get("/health", operation_id="auth_health")
def auth_health() -> dict:
    """
    Endpoint técnico para confirmar registro del módulo auth.
    No implementa login/registro.
    """
    return {"status": "ok"}
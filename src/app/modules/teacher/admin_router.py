from fastapi import APIRouter

router = APIRouter(
    prefix="/admin/teachers",
    tags=["admin-teachers"],
)

from pydantic import BaseModel, EmailStr, Field
from app.core.enums import UserRole, UserStatus


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    role: UserRole


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserPublic(BaseModel):   
    id: int
    email: EmailStr
    role: UserRole
    status: UserStatus


class RegisterResponse(BaseModel):
    user: UserPublic
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from app.core.enums import UserRole, UserStatus
from datetime import datetime


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
    model_config = ConfigDict(use_enum_values=True)
    
    id: int
    email: EmailStr
    role: UserRole
    status: UserStatus
    created_at: datetime
    

class RegisterResponse(BaseModel):
    user: UserPublic
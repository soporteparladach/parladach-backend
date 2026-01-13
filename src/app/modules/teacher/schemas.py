from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from app.core.enums import TeacherProfileStatus

class TeacherBase(BaseModel):
    user_id: int


class TeacherPublic(TeacherBase):
    id: int
    created_at: datetime


class TeacherAdmin(TeacherPublic):
    is_verified: bool


class TeacherProfileCreate(BaseModel):
    bio: Optional[str] = Field(default=None, max_length=2000)
    languages: Optional[List[str]] = None
    photo_url: Optional[str] = Field(default=None, max_length=2048)


class TeacherProfilePublic(BaseModel):
    id: int
    user_id: int
    bio: str
    languages: list[str]
    photo_url: str | None
    status: TeacherProfileStatus
    created_at: datetime
    updated_at: datetime


class TeacherProfileResponse(BaseModel):
    profile: TeacherProfilePublic
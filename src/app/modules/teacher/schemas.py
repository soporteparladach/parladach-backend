from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import List, Optional
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
    model_config = ConfigDict(from_attributes=True)

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

    @classmethod
    def from_orm_profile(cls, profile) -> "TeacherProfileResponse":
        return cls(profile=TeacherProfilePublic.model_validate(profile))


class TeacherProfileUpdate(BaseModel):
    bio: Optional[str] = Field(default=None, max_length=2000)
    languages: Optional[List[str]] = None
    photo_url: Optional[str] = Field(default=None, max_length=2048)


class TeacherProfileListResponse(BaseModel):
    items: List[TeacherProfilePublic]
    total: int
    limit: int
    offset: int


class PublicTeacherItem(BaseModel):
    teacher_profile_id: int
    bio: str
    languages: list[str]
    photo_url: Optional[str] = None
    display_name: Optional[str] = None  


class PublicTeachersResponse(BaseModel):
    items: list[PublicTeacherItem]
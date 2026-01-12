from pydantic import BaseModel
from datetime import datetime


class TeacherBase(BaseModel):
    user_id: int


class TeacherPublic(TeacherBase):
    id: int
    created_at: datetime


class TeacherAdmin(TeacherPublic):
    is_verified: bool

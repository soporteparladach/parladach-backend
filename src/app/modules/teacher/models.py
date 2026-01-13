from __future__ import annotations

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey,Text, DateTime, func, JSON
from app.core.base import Base
from sqlalchemy import Enum as SAEnum
from app.core.enums import TeacherProfileStatus


class Teacher(Base):
    __tablename__ = "teachers"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)


class TeacherProfile(Base):
    __tablename__ = "teacher_profiles"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Relación 1:1 con User (restricción 1:1 por unique)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )

    bio: Mapped[str] = mapped_column(Text, nullable=False, default="")
    languages: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    photo_url: Mapped[str | None] = mapped_column(Text, nullable=True)

    status: Mapped[TeacherProfileStatus] = mapped_column(
        SAEnum(TeacherProfileStatus, name="teacher_profile_status"),
        nullable=False,
        default=TeacherProfileStatus.DRAFT,
    )

    created_at: Mapped[object] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[object] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # relación ORM 1:1
    user = relationship("User", back_populates="teacher_profile", uselist=False)
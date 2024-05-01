from sqlalchemy import (
    String,
    Integer,
    UUID,
    TIMESTAMP,
    func,
    Boolean,
    JSON,
    ForeignKey,
    LargeBinary,
)
from typing import Annotated
from annotated_types import MinLen, MaxLen, LowerCase
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base, db
from pydantic import EmailStr
from datetime import datetime
from app.mixins import UserMixin
import bcrypt
import uuid


class User(Base):
    email: Mapped[EmailStr] = mapped_column(String(100), unique=True)
    username: Mapped[str] = mapped_column(String(60), unique=True)
    hashed_password: Mapped[str] = mapped_column(LargeBinary(60))
    registered_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, default=datetime.utcnow, server_default=func.now()
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    is_sponsor: Mapped[bool] = mapped_column(Boolean, default=False)
    role_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("role.id"), nullable=True
    )
    profile: Mapped["Profile"] = relationship(
        argument="Profile", back_populates="user", uselist=False
    )
    role: Mapped["Role"] = relationship(
        argument="Role", back_populates="user", uselist=False
    )

    def verify_password(self, password):
        return bcrypt.checkpw(password, self.hashed_password)

    def __str__(self):
        return f"{self.username}, {self.email}!"

    def __repr__(self):
        return str(self)


class Role(Base):
    name: Mapped[str] = mapped_column(String(64))
    permission_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("permission.id")
    )
    permission = relationship(
        argument="Permission", back_populates="role", uselist=False
    )
    user: Mapped["User"] = relationship(
        argument="User", back_populates="role", uselist=False
    )


class Profile(Base, UserMixin):
    _back_populates_field = "profile"
    _unique_field = True
    first_name: Mapped[str | None] = mapped_column(String(40))
    last_name: Mapped[str | None] = mapped_column(String(40))
    bio: Mapped[str | None]


class Permission(Base):
    name: Mapped[str] = mapped_column(String(64), unique=True)
    can_read: Mapped[bool] = mapped_column(Boolean, default=1)
    can_create: Mapped[bool] = mapped_column(Boolean, default=0)
    can_update: Mapped[bool] = mapped_column(Boolean, default=0)
    can_delete: Mapped[bool] = mapped_column(Boolean, default=0)
    role = relationship("Role", back_populates="permission")

    def __str__(self):
        return self.name

    def __repr__(self):
        return str(self)

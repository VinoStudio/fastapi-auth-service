from sqlalchemy.orm import declared_attr, mapped_column, Mapped, backref, relationship
from sqlalchemy import ForeignKey
from typing import TYPE_CHECKING
import bcrypt

if TYPE_CHECKING:
    from app.user.models import User


class UserMixin:
    _unique_field: bool = True
    _back_populates_field: str | None = None
    _nullable_field: bool = False

    @declared_attr
    def user_id(cls) -> Mapped[int]:
        return mapped_column(
            ForeignKey("user.id"),
            unique=cls._unique_field,
            nullable=cls._nullable_field,
        )

    @declared_attr
    def user(cls) -> Mapped["User"]:
        return relationship(argument="User", back_populates=cls._back_populates_field)

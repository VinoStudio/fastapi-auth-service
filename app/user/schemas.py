from pydantic import BaseModel, field_validator, EmailStr
from enum import Enum
from annotated_types import MinLen, MaxLen, LowerCase
from typing import Annotated
import uuid
from datetime import datetime
import re
from fastapi import HTTPException
import uuid
from enum import Enum


LETTER_MATCH_PATTERN = re.compile(r"^[а-яА-Яa-zA-Z\-]+$")


# UserValidation
class User(BaseModel):
    email: Annotated[EmailStr, MinLen(5), MaxLen(100)]
    username: Annotated[str, MinLen(3), MaxLen(50), LowerCase]


class UserRead(User):
    pass


class UserUpdate(BaseModel):
    email: Annotated[EmailStr, MinLen(5), MaxLen(100)] | None
    password: Annotated[str, MinLen(8), MaxLen(60)] | None


class UserCreate(User):
    password: Annotated[str, MinLen(8), MaxLen(60)]


class _User(User):
    id: uuid.UUID
    registered_at: datetime
    is_active: bool
    is_verified: bool


class Profile(BaseModel):
    first_name: str | None
    last_name: str | None
    bio: str | None

    @field_validator("first_name")
    @classmethod
    def validate_first_name(cls, value):
        if value:
            if not LETTER_MATCH_PATTERN.match(value):
                raise HTTPException(
                    status_code=422, detail="Name should contains only letters"
                )
            return value
        return value

    @field_validator("last_name")
    @classmethod
    def validate_last_name(cls, value):
        if value:
            if not LETTER_MATCH_PATTERN.match(value):
                raise HTTPException(
                    status_code=422, detail="Last name should contains only letters"
                )
            return value
        return value


class _Profile(Profile):
    id: uuid.UUID


class _Role(Enum):
    user = "user"
    moderator = "moderator"
    admin = "admin"


class _PermissionName(Enum):
    basic = "basic"
    moderator = "moderator"
    admin = "admin"


class _Permission(BaseModel):
    name: _PermissionName
    can_read: bool | None = True
    can_create: bool | None = False
    can_update: bool | None = False
    can_delete: bool | None = False

from pydantic import BaseModel, field_validator, EmailStr
from typing import Annotated
import uuid
from datetime import datetime


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

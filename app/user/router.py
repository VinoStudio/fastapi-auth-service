from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.user.models import User
from app.user.schemas import (
    UserCreate,
    UserRead,
    _Role,
    _Permission,
    _PermissionName,
    UserUpdate,
)
from app.user.utils import UserUtils, RoleUtils, PermissionUtils
from app.database import db
import uuid

router = APIRouter()


@router.post("/create/", response_model=UserRead)
async def create_user(user: UserCreate, user_utils: UserUtils = Depends(UserUtils)):
    return await user_utils.create_user(user)


@router.patch("/update/{user_username}", response_model=UserRead)
async def update_user(
    user_username: str,
    user_data: UserUpdate,
    user_utils: UserUtils = Depends(UserUtils),
):
    return await user_utils.update_user(user_data, user_username)


@router.delete("/delete/{user_username}")
async def delete_user(user_username: str, user_utils: UserUtils = Depends(UserUtils)):
    await user_utils.deactivate_user(user_username)
    return {"message": f"User {user_username} has been deleted"}


@router.delete("/delete_forever/{user_username}")
async def delete_user(user_username: str, user_utils: UserUtils = Depends(UserUtils)):
    await user_utils.delete_user(user_username)
    return {"message": f"User {user_username} has been deleted"}

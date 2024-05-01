from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.user.utils import UserUtils
from app.user.models import User
from app.user.schemas import UserCreate, UserRead, _Role, _Permission, _PermissionName
from app.user.utils import UserUtils, RoleUtils, PermissionUtils
from app.database import db
import uuid


router = APIRouter()

############################################
#   Create Role for User after Permission  #
############################################


@router.post("/roles/create/")
async def create_role(
    role: _Role,
    permission: _PermissionName,
    database: AsyncSession = Depends(db.get_session),
):
    permission = await PermissionUtils.get_permission(
        database=database, permission_name=permission.value
    )
    await RoleUtils.create_role(
        database=database, role_name=role, permission_id=permission.id
    )
    return {"message": "Role created"}


@router.post("/roles/{user_id}/")
async def add_role_to_user(
    user_id: uuid.UUID,
    role_name: _Role,
    database: AsyncSession = Depends(db.get_session),
):
    await RoleUtils.add_role_to_user(
        database=database, user_id=user_id, role_name=role_name.value
    )
    return {"message": "Role added"}


#################################
#   Create Permission for Role  #
#################################


@router.post("/permissions/")
async def add_permission(
    permission: _Permission, database: AsyncSession = Depends(db.get_session)
):
    await PermissionUtils.add_permission(database=database, permission=permission)
    return {"message": "Permission added"}

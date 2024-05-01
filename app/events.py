import uuid
from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import db
from app.user.utils import RoleUtils, PermissionUtils
from app.user.models import Role, Permission
from sqlalchemy import select, insert


@asynccontextmanager
async def permission_role_creation(app: FastAPI):
    async with db.async_session() as database:
        print(database)
        if not await RoleUtils.get_role_by_name(database=database, role_name="user"):
            permissions = {
                "user": {
                    "id": uuid.uuid4(),
                    "can_read": True,
                    "can_create": False,
                    "can_update": False,
                    "can_delete": False,
                },
                "moderator": {
                    "id": uuid.uuid4(),
                    "can_read": True,
                    "can_create": True,
                    "can_update": True,
                    "can_delete": False,
                },
                "admin": {
                    "id": uuid.uuid4(),
                    "can_read": True,
                    "can_create": True,
                    "can_update": True,
                    "can_delete": True,
                },
            }
            for name, permission in permissions.items():
                await database.execute(
                    insert(Permission).values(**permission, name=name)
                )
                await database.execute(
                    insert(Role).values(name=name, permission_id=permission.get("id"))
                )
            await database.commit()
    yield

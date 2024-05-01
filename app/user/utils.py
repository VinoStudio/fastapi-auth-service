import bcrypt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, select, Result, update, delete
from fastapi import HTTPException, status, Depends
from app.database import db
from typing import TYPE_CHECKING, Tuple
import bcrypt
from app.user.schemas import (
    UserCreate,
    UserRead,
    _Role,
    _Permission,
    _PermissionName,
    UserUpdate,
)
from sqlalchemy.exc import IntegrityError, DataError, InvalidRequestError, NoResultFound
import uuid
from app.user.models import Role, Profile, User, Permission
from app.auth.utils import AuthUtils
from app.tasks.celery import send_verification_email_task


class UserUtils:
    def __init__(self, database: AsyncSession = Depends(db.get_session)):
        self.db = database

    async def get_user(self, username) -> User:
        stmt = select(User).where(User.username == username)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        return user

    async def get_user_by_email(self, email) -> User:
        stmt = select(User).where(User.email == email)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()

        return user

    async def create_user(self, user: UserCreate) -> User:
        try:
            stmt = insert(User).values(
                **user.model_dump(exclude="password"),
                hashed_password=await self.hash_password(user.password),
                role_id=await RoleUtils.get_role_id_by_name(
                    database=self.db,
                    role_name="user",
                ),
            )
            await self.db.execute(stmt)
            await self.db.commit()
            user = await self.get_user(user.username)
            await self.create_profile(user_id=user.id)
            token = await AuthUtils.create_verification_token(user)
            send_verification_email_task.delay(
                email=user.email, username=user.username, token=token
            )
            return user

        except IntegrityError:
            raise HTTPException(
                status_code=422, detail="Username or Email already have been taken!"
            )

    async def create_profile(self, user_id):
        stmt = insert(Profile).values(user_id=user_id)
        await self.db.execute(stmt)
        await self.db.commit()

    async def update_user(self, user_data: UserUpdate, user_username) -> User:
        data = user_data.model_dump(exclude_unset=True)
        if password := data.pop("password", None):
            password = await self.hash_password(password)
        try:
            stmt = (
                update(User)
                .where(User.username == user_username)
                .values(**data, hashed_password=password)
            )
            await self.db.execute(stmt)
            await self.db.commit()
            return await self.get_user(user_username)
        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already have been taken!",
            )

    async def deactivate_user(self, user_username) -> User:
        stmt = (
            update(User).where(User.username == user_username).values(is_active=False)
        )
        await self.db.execute(stmt)
        await self.db.commit()
        return await self.get_user(user_username)

    async def delete_user(self, user_username):
        user = await self.get_user(user_username)
        stmt = delete(Profile).where(Profile.user_id == user.id)
        await self.db.execute(stmt)
        stmt = delete(User).where(User.id == user.id)
        await self.db.execute(stmt)
        await self.db.commit()

    @staticmethod
    async def hash_password(password) -> bytes:
        salt = bcrypt.gensalt()
        pwd_bytes: bytes = password.encode()
        return bcrypt.hashpw(pwd_bytes, salt)


class RoleUtils:
    @staticmethod
    async def create_role(
        database: AsyncSession, role_name: _Role, permission_id: uuid.UUID
    ) -> None:
        try:
            stmt = insert(Role).values(
                name=role_name.value, permission_id=permission_id
            )
            await database.execute(stmt)
            await database.commit()

        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Role already exists"
            )

    @staticmethod
    async def get_role_by_name(database: AsyncSession, role_name: str) -> Role | None:
        stmt = select(Role).where(Role.name == role_name)
        result = await database.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_role_id_by_name(database: AsyncSession, role_name: str) -> uuid.UUID:
        try:
            stmt = select(Role).where(Role.name == role_name)
            result = await database.execute(stmt)
            role = result.scalars().first()
            return role.id

        except NoResultFound:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Role not found"
            )

    @staticmethod
    async def update_user_role(
        database: AsyncSession, user_username: str, role_name: str
    ) -> None:
        try:
            stmt = (
                update(User)
                .where(User.username == user_username)
                .values(
                    role_id=await RoleUtils.get_role_id_by_name(database, role_name)
                )
            )
            await database.execute(stmt)
            await database.commit()

        except NoResultFound:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Role already exists"
            )


class PermissionUtils:
    @staticmethod
    async def add_permission(database: AsyncSession, permission: _Permission) -> None:
        data = permission.model_dump(exclude_unset=True)
        name = data.pop("name").value
        stmt = insert(Permission).values(**data, name=name)
        await database.execute(stmt)
        await database.commit()

    @staticmethod
    async def get_permission(
        database: AsyncSession, permission_name: str
    ) -> Permission | None:
        stmt = select(Permission).where(Permission.name == permission_name)
        result = await database.execute(stmt)
        return result.scalar_one_or_none()

import bcrypt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, select, Result, update, delete
from fastapi import HTTPException, status, Depends
import settings
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
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError
import uuid
from app.user.models import Role, Profile, User, Permission
from fastapi.security import (
    OAuth2PasswordRequestForm,
    OAuth2PasswordBearer,
    APIKeyCookie,
)
import jwt
from datetime import datetime, timedelta


auth_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
cookie_scheme = APIKeyCookie(name="access_token")


class AuthUtils:
    @staticmethod
    async def authenticate_user(
        database: AsyncSession, user_data: str, password: str | None
    ) -> User | None:
        try:
            if user_data.find("@") == -1:
                stmt = select(User).where(User.username == user_data)
            else:
                stmt = select(User).where(User.email == user_data)
            user = await database.execute(stmt)
            user = user.scalar_one_or_none()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect username",
                )
            if not user.verify_password(password.encode()):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect password",
                )
        except (DataError, NoResultFound, IntegrityError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect credentials or user does not exist",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user

    @staticmethod
    async def auth_user_by_token(database: AsyncSession, token: str) -> User:
        payload = await AuthUtils.decode_jwt_token(token)
        user_credentials = payload.get("sub")
        if payload["type"] != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
            )
        if payload["exp"] < datetime.utcnow().timestamp():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
            )
        if payload["sub"] is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )
        if user_credentials.find("@") == -1:
            stmt = select(User).where(User.username == user_credentials)
        else:
            stmt = select(User).where(User.email == user_credentials)
        user = await database.execute(stmt)
        user = user.scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not active",
            )
        return user

    @staticmethod
    async def get_current_user(
        database: AsyncSession = Depends(db.get_session),
        token: str = Depends(auth_scheme),
    ) -> User:
        user = await AuthUtils.auth_user_by_token(database, token)
        return user

    @staticmethod
    async def get_user_from_db(database: AsyncSession, user_data: str) -> User:
        stmt = select(User).where(User.email == user_data)
        user = await database.execute(stmt)
        return user.scalar_one_or_none()

    @staticmethod
    async def create_jwt_token(payload: dict) -> str:
        token = jwt.encode(
            payload,
            key=settings.RSASettings.private_key_path.read_text(),
            algorithm=settings.RSASettings.algorithm,
            headers={"alg": settings.RSASettings.algorithm, "typ": "JWT"},
        )
        return token

    @staticmethod
    async def decode_jwt_token(token: str) -> dict:
        return jwt.decode(
            token,
            key=settings.RSASettings.public_key_path.read_text(),
            algorithms=[settings.RSASettings.algorithm],
        )

    @staticmethod
    async def create_access_token(user: User):
        payload = {
            "type": "access",
            "sub": str(user.email),
            "exp": datetime.utcnow()
            + timedelta(minutes=settings.RSASettings.access_token_expire_minutes),
            "iat": datetime.utcnow(),
        }
        return await AuthUtils.create_jwt_token(payload)

    @staticmethod
    async def create_refresh_token(user: User):
        payload = {
            "type": "refresh",
            "sub": str(user.email),
            "exp": datetime.utcnow()
            + timedelta(minutes=settings.RSASettings.refresh_token_expire_minutes),
            "iat": datetime.utcnow(),
        }
        return await AuthUtils.create_jwt_token(payload)

    @staticmethod
    async def create_verification_token(user: User):
        payload = {
            "type": "verification",
            "sub": str(user.email),
            "exp": datetime.utcnow()
            + timedelta(minutes=settings.RSASettings.access_token_expire_minutes),
            "iat": datetime.utcnow(),
        }
        return await AuthUtils.create_jwt_token(payload)

    @staticmethod
    async def verify_user(
        database: AsyncSession,
        token: str,
    ) -> None:
        try:
            payload = await AuthUtils.decode_jwt_token(token)
            user_email = payload.get("sub")
            user = await AuthUtils.get_user_from_db(database, user_email)
            if user.is_verified:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User already verified",
                )
            user.is_verified = True
            user.is_active = True
            database.add(user)
            await database.commit()

        except (
            DataError,
            InvalidRequestError,
            NoResultFound,
            IntegrityError,
            InvalidTokenError,
        ) as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"{e}",
            )
        except ExpiredSignatureError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
            )

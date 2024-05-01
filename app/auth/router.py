from fastapi import APIRouter, Depends, HTTPException, status, Request, Response, Cookie
from fastapi.security import (
    OAuth2PasswordRequestForm,
    OAuth2PasswordBearer,
    APIKeyCookie,
    HTTPBearer,
)
from app.database import db
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.utils import AuthUtils, auth_scheme, cookie_scheme
from app.user.utils import UserUtils
from app.user.schemas import UserCreate, UserRead
from app.auth.schemas import Token
from app.user.models import User
from typing import Annotated

router = APIRouter()


@router.post("/sign_up")
async def sign_up(
    user: UserCreate,
    user_utils: UserUtils = Depends(UserUtils),
):
    user = await user_utils.create_user(user)
    return {
        "success": f"User {user.username} has been created",
        "message": f"Please, verify your email: {user.email}",
    }


@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    database: AsyncSession = Depends(db.get_session),
):
    user = await AuthUtils.authenticate_user(
        database, user_data=form_data.username, password=form_data.password
    )
    access_token = await AuthUtils.create_access_token(user)
    refresh_token = await AuthUtils.create_refresh_token(user)

    return Token(access_token=access_token, refresh_token=refresh_token)


@router.post("/login_token")
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    database: AsyncSession = Depends(db.get_session),
    response: Response = None,
):
    user = await AuthUtils.authenticate_user(
        database, user_data=form_data.username, password=form_data.password
    )
    access_token = await AuthUtils.create_access_token(user)
    refresh_token = await AuthUtils.create_refresh_token(user)

    response.set_cookie(key="access_token", value=access_token, httponly=True)
    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True)

    return Token(access_token=access_token, refresh_token=refresh_token)


@router.get("/me", response_model=UserRead)
async def get_user(
    current_user: User = Depends(AuthUtils.get_current_user),
):
    return current_user


@router.get("/current_user", response_model=UserRead)
async def get_current(
    token: str = Depends(cookie_scheme),
    database: AsyncSession = Depends(db.get_session),
):
    user = await AuthUtils.auth_user_by_token(token=token, database=database)
    return user


@router.get("/verify_email")
async def activate_user_account(
    token: str,
    username: str,
    database: AsyncSession = Depends(db.get_session),
):
    await AuthUtils.verify_user(database, token)
    return {"message": "User activated"}

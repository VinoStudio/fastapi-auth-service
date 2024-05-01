from sqlalchemy.orm import joinedload

from app.user.utils import UserUtils, RoleUtils, PermissionUtils
from app.auth.utils import AuthUtils
from app.user.models import User, Role, Profile
from app.database import test_db
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.user.schemas import UserCreate
from conftest import client
import pytest
from sqlalchemy import insert, update, select
from conftest import test_data_base
from conftest import async_client
import json
from tests.parametrize_data import user_create

pytestmark = pytest.mark.asyncio
parametrize = pytest.mark.parametrize


async def test_permission_role_user_creation(
    create_permission_and_role, create_user_for_tests
):
    await create_permission_and_role()
    await create_user_for_tests(
        username="admin",
        email="admin@admin.com",
        password="admin1234567",
        is_active=True,
        is_verified=True,
    )
    await create_user_for_tests(
        username="user",
        email="user@user.com",
        password="user1234567",
        is_active=True,
        is_verified=True,
    )
    await create_user_for_tests(
        username="moderator",
        email="moderator@moderator.com",
        password="moderator1234567",
    )
    return None


async def test_login_cookie():
    response = client.post(
        "/auth/login_token",
        data={
            "username": "admin",
            "password": "admin1234567",
        },
    )

    response_data = response.json()
    assert response.status_code == 200
    assert "access_token" in response_data
    assert "refresh_token" in response_data

    assert "access_token" in response.cookies

    cookies = {
        "access_token": response.cookies["access_token"],
        "refresh_token": response.cookies["refresh_token"],
    }

    response = client.get("/auth/current_user", cookies=cookies)
    response_data = response.json()

    print(response_data)
    assert response_data["username"] == "admin"
    assert response_data["email"] == "admin@admin.com"


async def test_login_jwt(async_client):
    response = client.post(
        url="auth/login",
        data={
            "username": "admin",
            "password": "admin1234567",
        },
    )

    response_data = response.json()
    assert response.status_code == 200
    assert "access_token" in response_data
    assert "refresh_token" in response_data

    header = {
        "accept": "application/json",
        "Authorization": f"Bearer {response_data['access_token']}",
    }

    response = await async_client.get(url="/auth/me", headers=header)

    response_data = response.json()

    assert response.status_code == 200
    assert response_data["username"] == "admin"
    assert response_data["email"] == "admin@admin.com"

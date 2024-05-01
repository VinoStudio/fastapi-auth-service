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
    )
    await create_user_for_tests(
        username="user",
        email="user@user.com",
        password="user1234567",
    )
    await create_user_for_tests(
        username="moderator",
        email="moderator@moderator.com",
        password="moderator1234567",
    )
    return None


async def test_user_verify(get_user_from_db):
    user = await get_user_from_db("admin")
    assert user.username == "admin"
    assert user.email == "admin@admin.com"
    assert user.is_active is False
    assert user.is_verified is False

    token = await AuthUtils.create_verification_token(user)
    response = client.get(f"/auth/verify_email?token={token}&username={user.username}")
    response_data = response.json()

    assert response.status_code == 200
    assert response_data["message"] == "User activated"

    user = await get_user_from_db("admin")
    assert user.is_active is True
    assert user.is_verified is True

    response = client.get(f"/auth/verify_email?token={token}&username={user.username}")
    response_data = response.json()

    assert response.status_code == 400
    assert response_data["detail"] == "User already verified"

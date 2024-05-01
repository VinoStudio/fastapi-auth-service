from sqlalchemy.orm import joinedload

from app.user.utils import UserUtils, RoleUtils, PermissionUtils
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
from tests.parametrize_data import user_create, user_update

pytestmark = pytest.mark.asyncio
parametrize = pytest.mark.parametrize


async def test_permission_role_creation(
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


@parametrize(*user_update)
async def test_user_update(
    user_username,
    userdata,
    expected_status,
    expected_response_detail,
):
    response = client.patch(
        url=f"/users/update/{user_username}",
        json=userdata,
    )
    assert response.status_code == expected_status
    assert response.json() == expected_response_detail

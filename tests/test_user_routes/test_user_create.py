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
from tests.parametrize_data import user_create

pytestmark = pytest.mark.asyncio
parametrize = pytest.mark.parametrize


async def test_permission_role_creation(create_permission_and_role):
    await create_permission_and_role()
    return None


def test_add_user():
    data = {
        "email": "admin@admin.com",
        "username": "admin",
        "password": "admin12345",
    }
    response = client.post(
        "/users/create/",
        json=data,
    )
    response_data = response.json()

    assert response.status_code == 200

    assert response_data["email"] == data["email"]
    assert response_data["username"] == data["username"]


async def test_user():
    async with test_data_base.async_session() as session:
        await RoleUtils.update_user_role(
            database=session, user_username="admin", role_name="admin"
        )
        stmt = (
            select(User)
            .where(User.username == "admin")
            .options(joinedload(User.role))
            .options(joinedload(User.profile))
        )
        result = await session.execute(stmt)
        user = result.scalars().all()
        assert user[0].email == "admin@admin.com"
        assert user[0].username == "admin"
        assert user[0].role.name == "admin"


async def test_get_user(get_user_from_db):
    user = await get_user_from_db("admin")
    assert user.username == "admin"
    assert user.email == "admin@admin.com"


async def test_existed_user_registration():
    data = {
        "email": "admin@admin.com",
        "username": "admin",
        "password": "admin12345",
    }
    response = client.post(
        "/users/create/",
        json=data,
    )
    assert response.status_code == 422
    assert response.json() == {"detail": "Username or Email already have been taken!"}


async def test_get_not_existed_user(get_user_from_db):
    user = await get_user_from_db("admin1")
    assert user is None


@parametrize(*user_create)
async def test_create_user(userdata, expected_status, expected_response_detail):
    response = client.post(
        "/users/create/",
        json=userdata,
    )
    assert response.status_code == expected_status
    assert response.json() == expected_response_detail

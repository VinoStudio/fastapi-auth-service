from fastapi.testclient import TestClient
from sqlalchemy.pool import NullPool
import pytest
import asyncio
from app.database import test_db, db, Base
from app.database import DataBase
from app.main import app
from settings import test_settings
from httpx import AsyncClient
from app.user.models import User, Role, Profile, Permission
from app.user.utils import UserUtils, RoleUtils
import uuid
from sqlalchemy import select, insert, update

test_data_base = DataBase(
    db_url=test_settings.test_db_url, echo=test_settings.test_db_echo, nullpool=NullPool
)

# Base.metadata.bind = test_db.engine

app.dependency_overrides[db.get_session] = test_data_base.get_session

client = TestClient(app)


@pytest.fixture(scope="session")
async def async_client():
    async with AsyncClient(app=app, base_url="http://test") as async_client:
        yield async_client


@pytest.fixture(scope="session")
async def event_loop(request):
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def create_test_database():
    async with test_db.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_db.engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="session")
async def get_user_from_db():
    async def get_user(username):
        async with test_data_base.async_session() as session:
            stmt = select(User).where(User.username == username)
            result = await session.execute(stmt)
            user = result.scalars().first()
            return user

    return get_user


@pytest.fixture(scope="session")
async def create_permission_and_role():
    async def permission_role_creation():
        async with test_db.async_session() as database:
            print(database)
            if not await RoleUtils.get_role_by_name(
                database=database, role_name="user"
            ):
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
                        "can_create": False,
                        "can_update": False,
                        "can_delete": False,
                    },
                    "admin": {
                        "id": uuid.uuid4(),
                        "can_read": True,
                        "can_create": False,
                        "can_update": False,
                        "can_delete": False,
                    },
                }
                for name, permission in permissions.items():
                    await database.execute(
                        insert(Permission).values(**permission, name=name)
                    )
                    await database.execute(
                        insert(Role).values(
                            name=name, permission_id=permission.get("id")
                        )
                    )
                await database.commit()

    return permission_role_creation


@pytest.fixture(scope="session")
async def create_user_for_tests():
    async def create_user(
        username, email, password, is_active=False, is_verified=False
    ):
        async with test_db.async_session() as database:
            await database.execute(
                insert(User).values(
                    username=username,
                    email=email,
                    hashed_password=await UserUtils.hash_password(password),
                    role_id=await RoleUtils.get_role_id_by_name(
                        database=database, role_name="user"
                    ),
                    is_active=is_active,
                    is_verified=is_verified,
                )
            )
            await database.commit()

    return create_user

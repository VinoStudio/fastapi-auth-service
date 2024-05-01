from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
    async_scoped_session,
)
from sqlalchemy.orm import declared_attr, DeclarativeBase, mapped_column, Mapped
from sqlalchemy import Integer, UUID
from app.settings import settings, test_settings
from sqlalchemy.pool import NullPool
import uuid
from redis import Redis


class Base(DeclarativeBase):
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )


class DataBase:
    def __init__(
        self, db_url: str, echo: bool = False, nullpool: NullPool | None = None
    ):
        if nullpool is not None:
            self.engine = create_async_engine(url=db_url, echo=echo, poolclass=nullpool)
        else:
            self.engine = create_async_engine(url=db_url, echo=echo)
        self.async_session = async_sessionmaker(
            self.engine,
            expire_on_commit=False,
            class_=AsyncSession,
            autoflush=False,
            autocommit=False,
        )

    async def get_session(self) -> AsyncSession:
        async with self.async_session() as session:
            yield session


redis = Redis(
    host=settings.redis.host,
    port=settings.redis.port,
    decode_responses=True,
)


db = DataBase(db_url=settings.db_url, echo=settings.db_echo)
test_db = DataBase(
    db_url=test_settings.test_db_url, echo=test_settings.test_db_echo, nullpool=NullPool
)

import asyncio
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from events_aggregator.core.config import settings
from events_aggregator.models.base import Base

engine = create_async_engine(
    settings.database_url,
    echo=False,
)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


_tables_created = False
_tables_lock = asyncio.Lock()


async def create_tables() -> None:
    global _tables_created

    if _tables_created:
        return

    async with _tables_lock:
        if _tables_created:
            return

        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)

        _tables_created = True


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    await create_tables()

    async with async_session_factory() as session:
        yield session

from functools import lru_cache

import sqlalchemy.ext.asyncio

from adapters.settings import get_fastapi_app_settings


@lru_cache
def create_async_engine() -> sqlalchemy.ext.asyncio.AsyncEngine:
    settings = get_fastapi_app_settings()
    return sqlalchemy.ext.asyncio.create_async_engine(
        settings.database_url,
        pool_pre_ping=True,
    )


@lru_cache
def create_session_factory() -> sqlalchemy.ext.asyncio.async_sessionmaker[sqlalchemy.ext.asyncio.AsyncSession]:
    engine = create_async_engine()
    return sqlalchemy.ext.asyncio.async_sessionmaker(
        engine,
        autoflush=False,
        future=True,
    )


def get_session() -> sqlalchemy.ext.asyncio.AsyncSession:
    session_factory = create_session_factory()
    return session_factory()

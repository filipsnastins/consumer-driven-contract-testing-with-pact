from functools import lru_cache

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from order_history.settings import get_settings


@lru_cache
def create_engine() -> AsyncEngine:
    settings = get_settings()
    return create_async_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
    )


@lru_cache
def create_session_factory() -> async_sessionmaker[AsyncSession]:
    engine = create_engine()
    return async_sessionmaker(
        engine,
        autoflush=False,
        future=True,
    )


def get_session() -> AsyncSession:
    session_factory = create_session_factory()
    return session_factory()

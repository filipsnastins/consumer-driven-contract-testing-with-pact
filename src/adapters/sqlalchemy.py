from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from adapters.settings import get_fastapi_app_settings

engine = create_async_engine(
    get_fastapi_app_settings().database_url,
    pool_pre_ping=True,
)

session_factory = async_sessionmaker(
    engine,
    autoflush=False,
    future=True,
)

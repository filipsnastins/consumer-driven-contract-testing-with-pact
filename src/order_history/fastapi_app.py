import uuid
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import strawberry
import structlog
from fastapi import FastAPI, Response
from pydantic import BaseModel
from strawberry.fastapi import GraphQLRouter

from adapters import sqlalchemy
from adapters.settings import get_fastapi_app_settings
from order_history import views
from order_history.graphql_schema import CustomerType
from order_history.pact import setup_pact_provider_state
from order_history.repository import Base, SQLAlchemyOrderHistoryRepository

logger: structlog.stdlib.BoundLogger = structlog.get_logger()


@strawberry.type
class Query:
    get_all_customers: list[CustomerType] = strawberry.field(resolver=views.get_all_customers)


graphql_schema = strawberry.Schema(query=Query)
graphql_app = GraphQLRouter(graphql_schema)  # type: ignore


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    engine = sqlalchemy.create_async_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("database_created")
    yield


app = FastAPI(title="service--order-history", lifespan=lifespan)
app.include_router(graphql_app, prefix="/graphql")


@app.get("/health")
def ping() -> dict[str, str]:
    return {"status": "ok"}


class ProviderState(BaseModel):
    consumer: str
    state: str | None = None
    states: list[str] = []


@app.post("/_pact/provider_states")
async def mock_pact_provider_states(provider_state: ProviderState, response: Response) -> dict:
    settings = get_fastapi_app_settings()
    if not settings.is_dev_env:
        response.status_code = 403
        return {}
    await setup_pact_provider_state(
        consumer=provider_state.consumer,
        state=provider_state.state,
        states=provider_state.states,
        correlation_id=uuid.uuid4(),
        repository=SQLAlchemyOrderHistoryRepository(sqlalchemy.create_session_factory()),
    )
    return {}

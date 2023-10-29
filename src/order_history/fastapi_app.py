import uuid

import strawberry
from fastapi import FastAPI, Response
from pydantic import BaseModel
from strawberry.fastapi import GraphQLRouter

from adapters import sqlalchemy
from adapters.settings import get_fastapi_app_settings
from order_history import views
from order_history.graphql_schema import CustomerType
from order_history.pact import setup_pact_provider_state
from order_history.repository import Base, SQLAlchemyOrderHistoryRepository


@strawberry.type
class Query:
    get_all_customers: list[CustomerType] = strawberry.field(resolver=views.get_all_customers)


graphql_schema = strawberry.Schema(query=Query)
graphql_app = GraphQLRouter(graphql_schema)  # type: ignore


app = FastAPI(title="service--order-history")
app.include_router(graphql_app, prefix="/graphql")


class ProviderState(BaseModel):
    consumer: str
    state: str | None = None


@app.get("/health")
def ping() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/_pact/provider_states")
async def mock_pact_provider_states(provider_state: ProviderState, response: Response) -> dict:
    settings = get_fastapi_app_settings()
    if not settings.is_dev_env:
        response.status_code = 403
        return {}
    engine = sqlalchemy.create_async_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await setup_pact_provider_state(
        consumer=provider_state.consumer,
        state=provider_state.state,
        states=[],
        correlation_id=uuid.uuid4(),
        repository=SQLAlchemyOrderHistoryRepository(sqlalchemy.create_session_factory()),
    )
    return {}

from contextlib import asynccontextmanager
from typing import AsyncGenerator

import strawberry
import structlog
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter

from order_history import use_cases
from order_history.database import create_engine
from order_history.models import Base
from order_history.schema import CustomerType

logger: structlog.stdlib.BoundLogger = structlog.get_logger()


@strawberry.type
class Query:
    get_all_customers: list[CustomerType] = strawberry.field(resolver=use_cases.Queries.get_all_customers)
    get_customer: CustomerType | None = strawberry.field(resolver=use_cases.Queries.get_customer)


schema = strawberry.Schema(Query)
graphql_app = GraphQLRouter(schema)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    async with create_engine().begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("database_initialized")
    yield


app = FastAPI(title="service--order-history", lifespan=lifespan)
app.include_router(graphql_app, prefix="/graphql")


@app.get("/health")
def ping() -> dict[str, str]:
    return {"status": "ok"}

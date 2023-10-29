import strawberry
import structlog
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter

from order_history import views
from order_history.schema import CustomerType

logger: structlog.stdlib.BoundLogger = structlog.get_logger()


@strawberry.type
class Query:
    get_all_customers: list[CustomerType] = strawberry.field(resolver=views.get_all_customers)
    get_customer: CustomerType | None = strawberry.field(resolver=views.get_customer)


schema = strawberry.Schema(query=Query)
graphql_app = GraphQLRouter(schema)


app = FastAPI(title="service--order-history")
app.include_router(graphql_app, prefix="/graphql")


@app.get("/health")
def ping() -> dict[str, str]:
    return {"status": "ok"}

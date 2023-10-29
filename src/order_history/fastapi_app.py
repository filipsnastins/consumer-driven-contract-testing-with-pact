import strawberry
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter

from order_history import views
from order_history.graphql_schema import CustomerType


@strawberry.type
class Query:
    get_all_customers: list[CustomerType] = strawberry.field(resolver=views.get_all_customers)


graphql_schema = strawberry.Schema(query=Query)
graphql_app = GraphQLRouter(graphql_schema)  # type: ignore


app = FastAPI(title="service--order-history")
app.include_router(graphql_app, prefix="/graphql")


@app.get("/health")
def ping() -> dict[str, str]:
    return {"status": "ok"}

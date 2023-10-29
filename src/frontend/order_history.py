import json
import uuid
from dataclasses import dataclass
from decimal import Decimal

import httpx
from stockholm import Money


@dataclass
class Order:
    id: uuid.UUID
    state: str
    order_total: Decimal


@dataclass
class Customer:
    id: uuid.UUID
    name: str
    orders: list[Order]


class OrderHistoryClient:
    def __init__(self, base_url: str) -> None:
        self._client = httpx.AsyncClient(base_url=base_url)

    async def get_all_customers(self) -> list[Customer]:
        graphql_query = "{getAllCustomers {id name orders {id orderTotal state}}}"
        response = await self._client.post("/graphql", json={"query": graphql_query})
        print(json.dumps({"query": graphql_query}))
        body = response.json()
        return [
            Customer(
                id=uuid.UUID(customer["id"]),
                name=customer["name"],
                orders=[
                    Order(
                        id=uuid.UUID(order["id"]),
                        order_total=Money.from_sub_units(order["orderTotal"]).as_decimal(),
                        state=order["state"],
                    )
                    for order in customer["orders"]
                ],
            )
            for customer in body["data"]["getAllCustomers"]
        ]

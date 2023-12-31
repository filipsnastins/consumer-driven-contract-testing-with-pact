import uuid
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum

import httpx
from stockholm import Money


class OrderNotFoundError(Exception):
    pass


class OrderState(Enum):
    CREATED = "CREATED"
    APPROVED = "APPROVED"


@dataclass
class Order:
    id: uuid.UUID
    customer_id: uuid.UUID
    order_total: Decimal
    state: OrderState


class OrderClient:
    def __init__(self, base_url: str) -> None:
        self._client = httpx.AsyncClient(base_url=base_url)

    async def create(self, customer_id: uuid.UUID, order_total: Decimal) -> Order:
        response = await self._client.post(
            "/order",
            json={
                "customer_id": str(customer_id),
                "order_total": int(Money(order_total).to_sub_units()),
            },
        )
        response.raise_for_status()
        body = response.json()
        return Order(
            id=uuid.UUID(body["id"]),
            customer_id=uuid.UUID(body["customer_id"]),
            order_total=Money.from_sub_units(body["order_total"]).as_decimal(),
            state=OrderState(body["state"]),
        )

    async def get(self, order_id: uuid.UUID) -> Order:
        response = await self._client.get(f"/order/{order_id}")
        if response.status_code == 404:
            raise OrderNotFoundError(order_id)
        response.raise_for_status()
        body = response.json()
        return Order(
            id=uuid.UUID(body["id"]),
            customer_id=uuid.UUID(body["customer_id"]),
            order_total=Money.from_sub_units(body["order_total"]).as_decimal(),
            state=OrderState(body["state"]),
        )

import uuid
from dataclasses import dataclass
from decimal import Decimal

import httpx
from stockholm import Money


@dataclass
class OrderCreatedResponse:
    order_id: uuid.UUID
    order_total: Decimal


class OrdersClient:
    def __init__(self, base_url: str) -> None:
        self._client = httpx.AsyncClient(base_url=base_url)

    async def create_order(self, customer_id: uuid.UUID, order_total: Decimal) -> OrderCreatedResponse:
        response = await self._client.post(
            "/order",
            json={
                "customer_id": str(customer_id),
                "order_total": int(Money(order_total).to_sub_units()),
            },
        )
        response.raise_for_status()
        body = response.json()
        return OrderCreatedResponse(
            order_id=uuid.UUID(body["order_id"]),
            order_total=Money.from_sub_units(body["order_total"]).as_decimal(),
        )

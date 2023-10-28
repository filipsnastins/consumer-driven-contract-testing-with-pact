import uuid
from asyncio import Protocol

import structlog
from stockholm import Money

from adapters.clients import DynamoDBClientFactory
from orders.domain import Order, OrderState

logger: structlog.stdlib.BoundLogger = structlog.get_logger()


class OrderRepository(Protocol):
    async def save(self, order: Order) -> None:
        ...

    async def get(self, order_id: uuid.UUID) -> Order | None:
        ...


class DynamoDBOrderRepository(OrderRepository):
    def __init__(self, table_name: str, client_factory: DynamoDBClientFactory) -> None:
        self._table_name = table_name
        self._client_factory = client_factory

    async def save(self, order: Order) -> None:
        async with self._client_factory() as client:
            await client.put_item(
                TableName=self._table_name,
                Item={
                    "PK": {"S": f"ORDER#{order.id}"},
                    "Id": {"S": str(order.id)},
                    "CustomerId": {"S": str(order.customer_id)},
                    "State": {"S": order.state.value},
                    "OrderTotal": {"N": str(Money(order.order_total).to_sub_units())},
                },
            )
            logger.info("order_repo__saved", order_id=order.id)

    async def get(self, order_id: uuid.UUID) -> Order | None:
        async with self._client_factory() as client:
            response = await client.get_item(
                TableName=self._table_name,
                Key={"PK": {"S": f"ORDER#{order_id}"}},
            )
            item = response.get("Item")
            if not item:
                logger.info("order_repo__not_found", order_id=order_id)
                return None
            return Order(
                id=uuid.UUID(item["Id"]["S"]),
                customer_id=uuid.UUID(item["CustomerId"]["S"]),
                state=OrderState[item["State"]["S"]],
                order_total=Money.from_sub_units(item["OrderTotal"]["N"]).as_decimal(),
            )

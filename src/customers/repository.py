import uuid
from typing import Protocol

import structlog
from stockholm import Money

from adapters.clients import DynamoDBClientFactory
from customers.domain import Customer

logger: structlog.stdlib.BoundLogger = structlog.get_logger()


class CustomerRepository(Protocol):
    async def save(self, customer: Customer) -> None:
        ...

    async def get(self, customer_id: uuid.UUID) -> Customer | None:
        ...


class DynamoDBCustomerRepository(CustomerRepository):
    def __init__(self, table_name: str, client_factory: DynamoDBClientFactory) -> None:
        self._table_name = table_name
        self._client_factory = client_factory

    async def save(self, customer: Customer) -> None:
        async with self._client_factory() as client:
            await client.put_item(
                TableName=self._table_name,
                Item={
                    "PK": {"S": f"CUSTOMER#{customer.id}"},
                    "Id": {"S": str(customer.id)},
                    "Name": {"S": customer.name},
                    "CreditReservations": {
                        "M": {
                            str(order_id): {"N": str(Money(order_total).to_sub_units())}
                            for order_id, order_total in customer.credit_reservations.items()
                        }
                    },
                },
            )
            logger.info("customer_repo__saved", customer_id=customer.id)

    async def get(self, customer_id: uuid.UUID) -> Customer | None:
        async with self._client_factory() as client:
            response = await client.get_item(
                TableName=self._table_name,
                Key={"PK": {"S": f"CUSTOMER#{customer_id}"}},
            )
            item = response.get("Item")
            if not item:
                logger.info("customer_repo__not_found", customer_id=customer_id)
                return None
            return Customer(
                id=uuid.UUID(item["Id"]["S"]),
                name=item["Name"]["S"],
                credit_reservations={
                    uuid.UUID(order_id): Money.from_sub_units(order_total["N"]).as_decimal()
                    for order_id, order_total in item["CreditReservations"]["M"].items()
                },
            )

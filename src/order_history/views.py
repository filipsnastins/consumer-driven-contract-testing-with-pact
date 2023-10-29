import uuid

import structlog

from adapters import sqlalchemy
from order_history.graphql_schema import CustomerType, OrderType
from order_history.repository import SQLAlchemyOrderHistoryRepository

logger: structlog.stdlib.BoundLogger = structlog.get_logger()


async def get_all_customers() -> list[CustomerType]:
    repository = SQLAlchemyOrderHistoryRepository(sqlalchemy.create_session_factory())
    customers = await repository.get_all_customers()
    logger.info("get_all_customers")
    return [
        CustomerType(
            id=str(customer.id),
            name=str(customer.name),
            orders=[
                OrderType(
                    id=str(order.id),
                    order_total=int(order.order_total),  # type: ignore
                    state=str(order.state),
                )
                for order in customer.orders
            ],
        )
        for customer in customers
    ]


async def get_customer(customer_id: uuid.UUID) -> CustomerType | None:
    repository = SQLAlchemyOrderHistoryRepository(sqlalchemy.create_session_factory())
    customer = await repository.get_customer(customer_id)
    log = logger.bind(customer_id=customer_id)
    if not customer:
        log.info("customer_not_found")
        return None
    log.info("get_customer")
    return CustomerType(
        id=str(customer.id),
        name=str(customer.name),
        orders=[
            OrderType(
                id=str(order.id),
                order_total=int(order.order_total),  # type: ignore
                state=str(order.state),
            )
            for order in customer.orders
        ],
    )

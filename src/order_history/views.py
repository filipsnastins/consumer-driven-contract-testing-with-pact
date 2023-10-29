import structlog
from stockholm import Money

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
                    state=str(order.state),
                    order_total=int(Money(order.order_total).to_sub_units()),
                )
                for order in customer.orders
            ],
        )
        for customer in customers
    ]

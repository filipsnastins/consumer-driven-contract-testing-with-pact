import uuid

from sqlalchemy import select

from adapters import sqlalchemy
from order_history.models import Customer
from order_history.schema import CustomerType, OrderType

# TODO: to get the benefits of GraphQL, use lazy loading and generators
# Read up on how to use GraphQL + SQLAlchemy


async def get_all_customers() -> list[CustomerType]:
    async with sqlalchemy.get_session() as session:
        stmt = select(Customer)
        customers = (await session.scalars(stmt.order_by(Customer.id))).unique()
        return [
            CustomerType(
                id=str(customer.id),
                name=str(customer.name),
                orders=[
                    OrderType(
                        id=str(order.id),
                        order_total=int(order.order_total),
                        state=str(order.state),
                    )
                    for order in customer.orders
                ],
            )
            for customer in customers
        ]


async def get_customer(customer_id: uuid.UUID) -> CustomerType | None:
    async with sqlalchemy.get_session() as session:
        stmt = select(Customer).where(Customer.id == customer_id)
        customer = await session.scalar(stmt)
        if not customer:
            return None
        return CustomerType(
            id=str(customer.id),
            name=str(customer.name),
            orders=[
                OrderType(
                    id=str(order.id),
                    order_total=int(order.order_total),
                    state=str(order.state),
                )
                for order in customer.orders
            ],
        )

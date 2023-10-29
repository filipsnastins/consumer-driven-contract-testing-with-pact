import structlog

from adapters.publisher import MessagePublisher
from orders.commands import ApproveOrderCommand, CreateOrderCommand
from orders.domain import Order, OrderNotFoundError
from orders.repository import OrderRepository

logger: structlog.stdlib.BoundLogger = structlog.get_logger()


async def create_order(cmd: CreateOrderCommand, repository: OrderRepository, publisher: MessagePublisher) -> Order:
    order, event = Order.create(
        correlation_id=cmd.correlation_id,
        customer_id=cmd.customer_id,
        order_total=cmd.order_total,
    )
    await repository.save(order)
    await publisher.publish(event)
    logger.info("order_created", order_id=order.id, customer_id=order.customer_id)
    return order


async def approve_order(cmd: ApproveOrderCommand, repository: OrderRepository) -> None:
    order = await repository.get(cmd.order_id)
    if not order:
        raise OrderNotFoundError(cmd.order_id)
    order.approve()
    await repository.save(order)
    logger.info("order_approved", order_id=cmd.order_id)

import structlog

from orders.adapters import MessagePublisher
from orders.commands import CreateOrderCommand
from orders.domain import Order
from orders.responses import CreateOrderResponse

logger: structlog.stdlib.BoundLogger = structlog.get_logger()


async def create_order(cmd: CreateOrderCommand, publisher: MessagePublisher) -> CreateOrderResponse:
    order, event = Order.create(
        correlation_id=cmd.correlation_id,
        customer_id=cmd.customer_id,
        order_total=cmd.order_total,
    )
    await publisher.publish(event, topic="order--created")
    logger.info("order_created", order_id=order.order_id, customer_id=order.customer_id)
    return CreateOrderResponse.from_order(order)

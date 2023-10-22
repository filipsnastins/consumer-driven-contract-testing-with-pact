from decimal import Decimal

import structlog

from adapters.publisher import MessagePublisher
from orders.commands import ApproveOrderCommand, CreateOrderCommand
from orders.domain import Order, OrderState
from orders.responses import CreateOrderResponse

logger: structlog.stdlib.BoundLogger = structlog.get_logger()


async def create_order(cmd: CreateOrderCommand, publisher: MessagePublisher) -> CreateOrderResponse:
    order, event = Order.create(
        correlation_id=cmd.correlation_id,
        customer_id=cmd.customer_id,
        order_total=cmd.order_total,
    )
    await publisher.publish(event)
    logger.info("order_created", order_id=order.order_id, customer_id=order.customer_id)
    return CreateOrderResponse.from_order(order)


async def approve_order(cmd: ApproveOrderCommand) -> None:
    order = Order(
        order_id=cmd.order_id,
        customer_id=cmd.customer_id,
        order_total=Decimal(0),
        state=OrderState.CREATED,
    )
    order.approve()
    logger.info("order_approved", order_id=cmd.order_id)

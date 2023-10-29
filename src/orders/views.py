import uuid

import structlog

from orders.domain import Order, OrderNotFoundError
from orders.repository import OrderRepository

logger: structlog.stdlib.BoundLogger = structlog.get_logger()


async def get_order(order_id: uuid.UUID, repository: OrderRepository) -> Order:
    order = await repository.get(order_id)
    if not order:
        logger.info("order_not_found", order_id=order_id)
        raise OrderNotFoundError(order_id)
    logger.info("get_order", order_id=order_id)
    return order

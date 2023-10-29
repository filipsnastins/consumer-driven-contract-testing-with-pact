import uuid

import structlog

from customers.domain import Customer, CustomerNotFoundError
from customers.repository import CustomerRepository

logger: structlog.stdlib.BoundLogger = structlog.get_logger()


async def get_customer(customer_id: uuid.UUID, repository: CustomerRepository) -> Customer:
    customer = await repository.get(customer_id)
    if customer is None:
        logger.info("customer_not_found", customer_id=customer_id)
        raise CustomerNotFoundError(customer_id)
    logger.info("get_customer", customer_id=customer_id)
    return customer

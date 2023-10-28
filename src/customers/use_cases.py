import uuid

import structlog

from adapters.publisher import MessagePublisher
from customers.commands import CreateCustomerCommand, ReserveCustomerCreditCommand
from customers.domain import Customer, CustomerNotFoundError
from customers.repository import CustomerRepository

logger: structlog.stdlib.BoundLogger = structlog.get_logger()


async def create_customer(cmd: CreateCustomerCommand, repository: CustomerRepository) -> Customer:
    customer = Customer.create(name=cmd.name)
    await repository.save(customer)
    logger.info("customer_created", customer_id=customer.id)
    return customer


async def get_customer(customer_id: uuid.UUID, repository: CustomerRepository) -> Customer:
    customer = await repository.get(customer_id)
    if customer is None:
        logger.info("customer_not_found", customer_id=customer_id)
        raise CustomerNotFoundError(customer_id)
    logger.info("get_customer", customer_id=customer_id)
    return customer


async def reserve_customer_credit(
    cmd: ReserveCustomerCreditCommand, repository: CustomerRepository, publisher: MessagePublisher
) -> None:
    customer = await repository.get(cmd.customer_id)
    if customer is None:
        raise CustomerNotFoundError(cmd.customer_id)
    event = customer.reserve_credit(order_id=cmd.order_id, order_total=cmd.order_total)
    await repository.save(customer)
    await publisher.publish(event)
    logger.info("customer_credit_reserved", customer_id=cmd.customer_id, order_id=cmd.order_id)

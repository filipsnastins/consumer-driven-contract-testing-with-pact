import structlog

from adapters.publisher import MessagePublisher
from customers.commands import CreateCustomerCommand, ReserveCustomerCreditCommand
from customers.domain import Customer, CustomerNotFoundError
from customers.repository import CustomerRepository

logger: structlog.stdlib.BoundLogger = structlog.get_logger()


async def create_customer(
    cmd: CreateCustomerCommand, repository: CustomerRepository, publisher: MessagePublisher
) -> Customer:
    customer, event = Customer.create(correlation_id=cmd.correlation_id, name=cmd.name)
    await repository.save(customer)
    await publisher.publish(event)
    logger.info("customer_created", customer_id=customer.id)
    return customer


async def reserve_customer_credit(
    cmd: ReserveCustomerCreditCommand, repository: CustomerRepository, publisher: MessagePublisher
) -> None:
    customer = await repository.get(cmd.customer_id)
    if customer is None:
        raise CustomerNotFoundError(cmd.customer_id)
    event = customer.reserve_credit(
        correlation_id=cmd.correlation_id,
        order_id=cmd.order_id,
        order_total=cmd.order_total,
    )
    await repository.save(customer)
    await publisher.publish(event)
    logger.info("customer_credit_reserved", customer_id=cmd.customer_id, order_id=cmd.order_id)

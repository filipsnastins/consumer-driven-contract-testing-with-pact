import structlog

from customers.adapters import MessagePublisher
from customers.commands import ReserveCustomerCreditCommand
from customers.domain import Customer

logger: structlog.stdlib.BoundLogger = structlog.get_logger()


async def reserve_customer_credit(cmd: ReserveCustomerCreditCommand, publisher: MessagePublisher) -> None:
    customer = Customer(customer_id=cmd.customer_id)
    event = customer.reserve_credit(order_id=cmd.order_id, order_total=cmd.order_total)
    await publisher.publish(event.to_proto(), topic="customer--credit-reserved")
    logger.info("customer_credit_reserved", order_id=cmd.order_id)

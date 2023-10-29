import structlog

from order_history.commands import RegisterNewCustomerCommand, RegisterNewOrderCommand, RegisterOrderApprovedCommand
from order_history.repository import OrderHistoryRepository

logger: structlog.stdlib.BoundLogger = structlog.get_logger()


async def register_new_customer(cmd: RegisterNewCustomerCommand, repository: OrderHistoryRepository) -> None:
    await repository.register_new_customer(customer_id=cmd.customer_id, name=cmd.name)
    logger.info("customer_created", customer_id=cmd.customer_id)


async def register_new_order(cmd: RegisterNewOrderCommand, repository: OrderHistoryRepository) -> None:
    await repository.register_new_order(
        customer_id=cmd.customer_id,
        order_id=cmd.order_id,
        state="CREATED",
        order_total=cmd.order_total,
    )
    logger.info("order_created", order_id=cmd.order_id, customer_id=cmd.customer_id)


async def register_order_approved(cmd: RegisterOrderApprovedCommand, repository: OrderHistoryRepository) -> None:
    await repository.update_order_state(
        order_id=cmd.order_id,
        state="APPROVED",
    )
    logger.info("order_approved", order_id=cmd.order_id)

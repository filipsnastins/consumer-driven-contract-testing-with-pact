import uuid
from decimal import Decimal
from typing import Protocol

import structlog

from order_history import use_cases
from order_history.commands import RegisterNewCustomerCommand, RegisterNewOrderCommand
from order_history.repository import OrderHistoryRepository

logger: structlog.stdlib.BoundLogger = structlog.get_logger()


class PactProviderStateSetupHandler(Protocol):
    async def __call__(self, correlation_id: uuid.UUID, repository: OrderHistoryRepository) -> None:
        ...


async def mock_customer_d3100f4f_exists(correlation_id: uuid.UUID, repository: OrderHistoryRepository) -> None:
    await use_cases.register_new_customer(
        RegisterNewCustomerCommand(
            customer_id=uuid.UUID("d3100f4f-c8a7-4207-a5e2-40aa122b4b33"),
            name="John Doe",
        ),
        repository,
    )
    await use_cases.register_new_order(
        RegisterNewOrderCommand(
            order_id=uuid.UUID("f408cf27-8c53-486e-89f6-f0b45355b3ed"),
            customer_id=uuid.UUID("d3100f4f-c8a7-4207-a5e2-40aa122b4b33"),
            order_total=Decimal("123.99"),
        ),
        repository,
    )
    logger.info("mock_customer_d3100f4f_exists")


MAPPING: dict[str, PactProviderStateSetupHandler] = {
    "A customer d3100f4f exists": mock_customer_d3100f4f_exists,
}


async def setup_pact_provider_state(
    consumer: str,
    state: str | None,
    states: list[str],
    correlation_id: uuid.UUID,
    repository: OrderHistoryRepository,
) -> None:
    log = logger.bind(consumer=consumer, state=state, states=states)
    if state is None:
        log.info("pact_no_state_to_setup")
        return
    log.info("pact_setup_provider_state")
    handler = MAPPING[state]
    await handler(correlation_id, repository)

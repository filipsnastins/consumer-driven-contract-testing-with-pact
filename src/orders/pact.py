import uuid
from decimal import Decimal
from typing import Protocol
from unittest.mock import AsyncMock, patch

import structlog

from adapters.publisher import MessagePublisher
from orders import use_cases
from orders.commands import CreateOrderCommand
from orders.repository import OrderRepository

logger: structlog.stdlib.BoundLogger = structlog.get_logger()


class PactProviderStateSetupHandler(Protocol):
    async def __call__(
        self, correlation_id: uuid.UUID, repository: OrderRepository, publisher: MessagePublisher
    ) -> None:
        ...


async def mock_order_f408cf27_exist(
    correlation_id: uuid.UUID, repository: OrderRepository, publisher: MessagePublisher
) -> None:
    cmd = CreateOrderCommand(
        correlation_id=correlation_id,
        customer_id=uuid.uuid4(),
        order_total=Decimal("100.99"),
    )
    with patch("orders.domain.uuid.uuid4", return_value=uuid.UUID("f408cf27-8c53-486e-89f6-f0b45355b3ed")):
        await use_cases.create_order(cmd, repository, AsyncMock())
    logger.info("mock_order_f408cf27_exist")


MAPPING: dict[str, PactProviderStateSetupHandler] = {
    "An order f408cf27 exists": mock_order_f408cf27_exist,
}


async def setup_pact_provider_state(
    consumer: str,
    state: str,
    states: list[str],
    correlation_id: uuid.UUID,
    repository: OrderRepository,
    publisher: MessagePublisher,
) -> None:
    log = logger.bind(consumer=consumer, state=state, states=states)
    if state is None:
        log.info("pact_no_state_to_setup")
        return
    log.info("pact_setup_provider_state")
    handler = MAPPING[state]
    await handler(correlation_id, repository, publisher)

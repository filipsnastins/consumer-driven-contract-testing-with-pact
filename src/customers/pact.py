import uuid
from typing import Protocol
from unittest.mock import AsyncMock, patch

import structlog

from adapters.publisher import MessagePublisher
from customers import use_cases
from customers.commands import CreateCustomerCommand
from customers.repository import CustomerRepository

logger: structlog.stdlib.BoundLogger = structlog.get_logger()


class PactProviderStateSetupHandler(Protocol):
    async def __call__(
        self, correlation_id: uuid.UUID, repository: CustomerRepository, publisher: MessagePublisher
    ) -> None:
        ...


async def mock_customer_d3100f4f_exists(
    correlation_id: uuid.UUID, repository: CustomerRepository, publisher: MessagePublisher
) -> None:
    cmd = CreateCustomerCommand(
        correlation_id=correlation_id,
        name="John Doe",
    )
    with patch("customers.domain.uuid.uuid4", return_value=uuid.UUID("d3100f4f-c8a7-4207-a5e2-40aa122b4b33")):
        await use_cases.create_customer(cmd, repository, AsyncMock())
    logger.info("mock_customer_d3100f4f_exists")


MAPPING: dict[str, PactProviderStateSetupHandler] = {
    "A customer d3100f4f exists": mock_customer_d3100f4f_exists,
}


async def setup_pact_provider_state(
    consumer: str,
    state: str,
    states: list[str],
    correlation_id: uuid.UUID,
    repository: CustomerRepository,
    publisher: MessagePublisher,
) -> None:
    log = logger.bind(consumer=consumer, state=state, states=states)
    if state is None:
        log.info("pact_no_state_to_setup")
        return
    log.info("pact_setup_provider_state")
    handler = MAPPING[state]
    await handler(correlation_id, repository, publisher)

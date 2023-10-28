import uuid
from decimal import Decimal
from typing import Awaitable, Callable
from unittest.mock import AsyncMock, patch

import structlog
import tomodachi
from aiohttp import web

from adapters import clients, dynamodb
from orders import use_cases
from orders.commands import CreateOrderCommand
from orders.repository import DynamoDBOrderRepository

logger: structlog.stdlib.BoundLogger = structlog.get_logger()


async def mock_order_f408cf27_exist(correlation_id: uuid.UUID, repo: DynamoDBOrderRepository) -> None:
    cmd = CreateOrderCommand(
        correlation_id=correlation_id,
        customer_id=uuid.uuid4(),
        order_total=Decimal("100.99"),
    )
    with patch("orders.domain.uuid.uuid4", return_value=uuid.UUID("f408cf27-8c53-486e-89f6-f0b45355b3ed")):
        await use_cases.create_order(cmd, repo, AsyncMock())
    logger.info("mock_order_f408cf27_exist")


MAPPING: dict[str, Callable[[uuid.UUID, DynamoDBOrderRepository], Awaitable]] = {
    "An order f408cf27 exists": mock_order_f408cf27_exist,
}


class PactProviderStateService:
    @tomodachi.http("POST", r"/_pact/provider_states")
    async def mock_pact_provider_states(self, request: web.Request, correlation_id: uuid.UUID) -> web.Response:
        repo = DynamoDBOrderRepository(dynamodb.get_table_name(), clients.get_dynamodb_client)

        body = await request.json()
        consumer = body["consumer"]
        state = body["state"]
        states = body["states"]
        log = logger.bind(consumer=consumer, state=state, states=states)

        if state is None:
            log.info("pact_no_state_to_setup")
            return web.json_response({})

        log.info("pact_setup_provider_state")
        handler = MAPPING[state]
        await handler(correlation_id, repo)
        return web.json_response({})

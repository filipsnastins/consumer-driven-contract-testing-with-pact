import uuid
from asyncio import AbstractEventLoop
from decimal import Decimal

import pytest
from pact import MessageProvider
from pytest_mock import MockerFixture

from orders import use_cases
from orders.commands import ApproveOrderCommand, CreateOrderCommand
from tests.fakes import InMemoryMessagePublisher, InMemoryOrderRepository
from tests.pact_helpers import proto_to_dict

DEFAULT_OPTS = {
    "broker_url": "http://localhost:9292",
    "broker_username": "pactbroker",
    "broker_password": "pactbroker",
    "publish_verification_results": True,
    "publish_version": "0.0.1",
}


async def order_created_message_provider() -> dict:
    repository = InMemoryOrderRepository([])
    publisher = InMemoryMessagePublisher([])

    await use_cases.create_order(
        CreateOrderCommand(
            correlation_id=uuid.UUID("58b587a2-860c-4c4a-a9af-70457ffae596"),
            customer_id=uuid.UUID("1e5df855-a757-4aa5-a55f-2ddf6930b250"),
            order_total=Decimal("123.99"),
        ),
        repository,
        publisher,
    )

    [message] = publisher.messages
    return proto_to_dict(message.to_proto())


async def order_approved_message_provider(mocker: MockerFixture) -> dict:
    repository = InMemoryOrderRepository([])
    publisher = InMemoryMessagePublisher([])
    mocker.patch("orders.domain.uuid.uuid4", return_value=uuid.UUID("f408cf27-8c53-486e-89f6-f0b45355b3ed"))
    order = await use_cases.create_order(
        CreateOrderCommand(
            correlation_id=uuid.UUID("58b587a2-860c-4c4a-a9af-70457ffae596"),
            customer_id=uuid.UUID("1e5df855-a757-4aa5-a55f-2ddf6930b250"),
            order_total=Decimal("123.99"),
        ),
        repository,
        publisher,
    )
    publisher.clear()

    await use_cases.approve_order(
        ApproveOrderCommand(
            correlation_id=uuid.UUID("58b587a2-860c-4c4a-a9af-70457ffae596"),
            customer_id=uuid.UUID("1e5df855-a757-4aa5-a55f-2ddf6930b250"),
            order_id=order.id,
        ),
        repository,
        publisher,
    )

    [message] = publisher.messages
    return proto_to_dict(message.to_proto())


@pytest.mark.parametrize("consumer", ["service-customers--sns"])
def test_verify_consumer_contracts(event_loop: AbstractEventLoop, mocker: MockerFixture, consumer: str) -> None:
    provider = MessageProvider(
        message_providers={
            "New order is created": lambda: event_loop.run_until_complete(order_created_message_provider()),
            "A created order has been approved": lambda: event_loop.run_until_complete(
                order_approved_message_provider(mocker)
            ),
        },
        provider="service-orders--sns",
        consumer=consumer,
        pact_dir="pacts",
    )

    with provider:
        provider.verify_with_broker(**DEFAULT_OPTS)

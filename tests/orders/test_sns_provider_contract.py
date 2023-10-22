import uuid
from asyncio import AbstractEventLoop
from decimal import Decimal

from fakes import InMemoryMessagePublisher
from pact import MessageProvider

from adapters import proto
from orders import use_cases
from orders.commands import CreateOrderCommand
from tests.pact_helpers import proto_to_dict

DEFAULT_OPTS = {
    "broker_url": "http://localhost:9292",
    "broker_username": "pactbroker",
    "broker_password": "pactbroker",
    "publish_verification_results": True,
    "publish_version": "0.0.1",
}


async def order_created_message_provider() -> dict:
    publisher = InMemoryMessagePublisher([])

    cmd = CreateOrderCommand(
        correlation_id=uuid.UUID("58b587a2-860c-4c4a-a9af-70457ffae596"),
        customer_id=uuid.UUID("1e5df855-a757-4aa5-a55f-2ddf6930b250"),
        order_total=Decimal("123.99"),
    )
    await use_cases.create_order(cmd, publisher=publisher)

    [message] = publisher.messages
    assert isinstance(message.to_proto(), proto.OrderCreated)
    return proto_to_dict(message.to_proto())


def test_verify_service_customers_consumer(event_loop: AbstractEventLoop) -> None:
    provider = MessageProvider(
        message_providers={
            "New order is created": lambda: event_loop.run_until_complete(order_created_message_provider()),
        },
        provider="service-orders--sns",
        consumer="service-customers--sns",
        pact_dir="pacts",
    )

    with provider:
        provider.verify_with_broker(**DEFAULT_OPTS)

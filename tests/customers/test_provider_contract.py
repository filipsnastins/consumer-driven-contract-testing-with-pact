import uuid
from asyncio import AbstractEventLoop
from decimal import Decimal

from fakes import InMemoryMessagePublisher
from pact import MessageProvider

from adapters import proto
from customers import use_cases
from customers.commands import ReserveCustomerCreditCommand
from tests.pact_helpers import proto_to_dict

DEFAULT_OPTS = {
    "broker_url": "http://localhost:9292",
    "broker_username": "pactbroker",
    "broker_password": "pactbroker",
    "publish_verification_results": True,
    "publish_version": "0.0.1",
}


async def customer_credit_reserved_message_provider() -> dict:
    publisher = InMemoryMessagePublisher([])

    cmd = ReserveCustomerCreditCommand(
        correlation_id=uuid.UUID("58b587a2-860c-4c4a-a9af-70457ffae596"),
        customer_id=uuid.UUID("1e5df855-a757-4aa5-a55f-2ddf6930b250"),
        order_id=uuid.UUID("f408cf27-8c53-486e-89f6-f0b45355b3ed"),
        order_total=Decimal("123.99"),
    )
    await use_cases.reserve_customer_credit(cmd, publisher=publisher)

    [message] = publisher.messages
    assert isinstance(message, proto.CustomerCreditReserved)
    return proto_to_dict(message)


def test_verify_service_orders_consumer(event_loop: AbstractEventLoop) -> None:
    message_providers = {
        "Customer credit is reserved for created order": lambda: event_loop.run_until_complete(
            customer_credit_reserved_message_provider()
        ),
    }
    provider = MessageProvider(
        message_providers=message_providers,
        provider="service-customers",
        consumer="service-orders",
        pact_dir="pacts",
    )

    with provider:
        provider.verify_with_broker(**DEFAULT_OPTS)

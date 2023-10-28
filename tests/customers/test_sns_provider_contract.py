import uuid
from asyncio import AbstractEventLoop
from decimal import Decimal

from pact import MessageProvider
from pytest_mock import MockerFixture

from customers import use_cases
from customers.commands import CreateCustomerCommand, ReserveCustomerCreditCommand
from tests.fakes import InMemoryCustomerRepository, InMemoryMessagePublisher
from tests.pact_helpers import proto_to_dict

DEFAULT_OPTS = {
    "broker_url": "http://localhost:9292",
    "broker_username": "pactbroker",
    "broker_password": "pactbroker",
    "publish_verification_results": True,
    "publish_version": "0.0.1",
}


async def customer_credit_reserved_message_provider(mocker: MockerFixture) -> dict:
    repo = InMemoryCustomerRepository([])
    publisher = InMemoryMessagePublisher([])
    mocker.patch("customers.domain.uuid.uuid4", return_value=uuid.UUID("1e5df855-a757-4aa5-a55f-2ddf6930b250"))
    customer = await use_cases.create_customer(CreateCustomerCommand(name="John Doe"), repo)

    await use_cases.reserve_customer_credit(
        ReserveCustomerCreditCommand(
            customer_id=customer.id,
            order_id=uuid.UUID("f408cf27-8c53-486e-89f6-f0b45355b3ed"),
            order_total=Decimal("123.99"),
        ),
        repo,
        publisher,
    )

    [message] = publisher.messages
    return proto_to_dict(message.to_proto())


def test_verify_service_orders_consumer(event_loop: AbstractEventLoop, mocker: MockerFixture) -> None:
    provider = MessageProvider(
        message_providers={
            "Customer credit is reserved for created order": lambda: event_loop.run_until_complete(
                customer_credit_reserved_message_provider(mocker)
            ),
        },
        provider="service-customers--sns",
        consumer="service-orders--sns",
        pact_dir="pacts",
    )

    with provider:
        provider.verify_with_broker(**DEFAULT_OPTS)

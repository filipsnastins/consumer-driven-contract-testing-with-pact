import uuid
from asyncio import AbstractEventLoop
from decimal import Decimal

import pytest
from pytest_mock import MockerFixture

from customers import use_cases
from customers.commands import CreateCustomerCommand, ReserveCustomerCreditCommand
from tests.fakes import InMemoryCustomerRepository, InMemoryMessagePublisher
from tests.pact_helpers import MessageProvider, proto_to_dict

pytestmark = [pytest.mark.customers__sns(), pytest.mark.provider(), pytest.mark.pactflow(), pytest.mark.order(2)]


async def customer_created_message_provider(mocker: MockerFixture) -> dict:
    repository = InMemoryCustomerRepository([])
    publisher = InMemoryMessagePublisher([])
    mocker.patch("customers.domain.uuid.uuid4", return_value=uuid.UUID("1e5df855-a757-4aa5-a55f-2ddf6930b250"))

    await use_cases.create_customer(
        CreateCustomerCommand(
            correlation_id=uuid.UUID("293178a5-4838-4e6a-8d63-18062093027e"),
            name="John Doe",
        ),
        repository,
        publisher,
    )

    [message] = publisher.messages
    return proto_to_dict(message.to_proto())


async def customer_credit_reserved_message_provider(mocker: MockerFixture) -> dict:
    repository = InMemoryCustomerRepository([])
    publisher = InMemoryMessagePublisher([])
    mocker.patch("customers.domain.uuid.uuid4", return_value=uuid.UUID("1e5df855-a757-4aa5-a55f-2ddf6930b250"))
    customer = await use_cases.create_customer(
        CreateCustomerCommand(
            correlation_id=uuid.UUID("293178a5-4838-4e6a-8d63-18062093027e"),
            name="John Doe",
        ),
        repository,
        publisher,
    )
    publisher.clear()

    await use_cases.reserve_customer_credit(
        ReserveCustomerCreditCommand(
            correlation_id=uuid.UUID("293178a5-4838-4e6a-8d63-18062093027e"),
            customer_id=customer.id,
            order_id=uuid.UUID("f408cf27-8c53-486e-89f6-f0b45355b3ed"),
            order_total=Decimal("123.99"),
        ),
        repository,
        publisher,
    )

    [message] = publisher.messages
    return proto_to_dict(message.to_proto())


def test_verify_consumer_contracts(event_loop: AbstractEventLoop, mocker: MockerFixture) -> None:
    # Arrange
    provider = MessageProvider(
        message_providers={
            "New customer is created": lambda: event_loop.run_until_complete(customer_created_message_provider(mocker)),
            "Customer credit is reserved for created order": lambda: event_loop.run_until_complete(
                customer_credit_reserved_message_provider(mocker)
            ),
        },
        provider="service-customers--sns",
        # Running tests for all consumers with `provider.verify_with_broker`
        # When using `provider.verify`, make sure to include the consumer name
        consumer="",
        pact_dir="pacts",
    )

    # Act & Assert not raised
    with provider:
        provider.verify_with_broker()

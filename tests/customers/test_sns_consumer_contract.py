import uuid

import pytest
import pytest_asyncio
from pact import Format, Like, MessageConsumer, MessagePact, Provider, Term
from pytest_mock import MockerFixture

from adapters import proto
from customers import use_cases
from customers.commands import CreateCustomerCommand
from customers.tomodachi_app import ServiceCustomers
from tests.fakes import InMemoryCustomerRepository, InMemoryMessagePublisher
from tests.pact_helpers import create_proto_from_pact


@pytest.fixture()
def pact() -> MessagePact:
    return MessageConsumer("service-customers--sns", version="0.0.1").has_pact_with(
        Provider("service-orders--sns"),
        publish_to_broker=True,
        broker_base_url="http://localhost:9292",
        broker_username="pactbroker",
        broker_password="pactbroker",
        pact_dir="pacts",
    )


@pytest.fixture()
def repository() -> InMemoryCustomerRepository:
    return InMemoryCustomerRepository([])


@pytest.fixture()
def publisher() -> InMemoryMessagePublisher:
    return InMemoryMessagePublisher([])


@pytest_asyncio.fixture()
async def service(
    mocker: MockerFixture, repository: InMemoryCustomerRepository, publisher: InMemoryMessagePublisher
) -> ServiceCustomers:
    service = ServiceCustomers()
    mocker.patch.object(service, "_repository", repository)
    mocker.patch.object(service, "_publisher", publisher)
    return service


@pytest.mark.asyncio()
async def test_consume_order_created_event(
    pact: MessagePact,
    mocker: MockerFixture,
    service: ServiceCustomers,
    repository: InMemoryCustomerRepository,
    publisher: InMemoryMessagePublisher,
) -> None:
    mocker.patch("customers.domain.uuid.uuid4", return_value=uuid.UUID("d3100f4f-c8a7-4207-a5e2-40aa122b4b33"))
    customer = await use_cases.create_customer(
        CreateCustomerCommand(
            correlation_id=uuid.UUID("293178a5-4838-4e6a-8d63-18062093027e"),
            name="John Doe",
        ),
        repository,
        publisher,
    )

    expected_message = {
        "correlation_id": Term(Format.Regexes.uuid.value, "23b2c005-a914-41ab-92d7-d8d4d8e98020"),
        "customer_id": Term(Format.Regexes.uuid.value, str(customer.id)),
        "order_id": Term(Format.Regexes.uuid.value, "cc935616-e439-45a9-89ed-c6ef32bbc59e"),
        "order_total": Like(
            {
                "units": "100",
                "nanos": 990000000,
            }
        ),
    }
    pact.given("New order is created").expects_to_receive("OrderCreated event").with_content(expected_message)

    with pact:
        data = create_proto_from_pact(proto.OrderCreated, expected_message)
        await service.order_created_handler(data, correlation_id=uuid.UUID("23b2c005-a914-41ab-92d7-d8d4d8e98020"))

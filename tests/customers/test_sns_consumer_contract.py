import uuid

import pytest
import pytest_asyncio
from pact import Format, Like, MessageConsumer, MessagePact, Provider, Term
from pytest_mock import MockerFixture

from adapters import proto
from customers.app import Service
from tests.fakes import InMemoryMessagePublisher
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


@pytest_asyncio.fixture()
async def service(mocker: MockerFixture) -> Service:
    s = Service()
    await s._start_service()
    mocker.patch.object(s, "_publisher", InMemoryMessagePublisher([]))
    return s


@pytest.mark.asyncio()
async def test_order_created(pact: MessagePact, service: Service) -> None:
    expected_message = {
        "correlation_id": Term(Format.Regexes.uuid.value, "23b2c005-a914-41ab-92d7-d8d4d8e98020"),
        "customer_id": Term(Format.Regexes.uuid.value, "d3100f4f-c8a7-4207-a5e2-40aa122b4b33"),
        "order_id": Term(Format.Regexes.uuid.value, "cc935616-e439-45a9-89ed-c6ef32bbc59e"),
        "order_total": Like(
            {
                "units": "100",
                "nanos": 990000000,
            }
        ),
    }

    pact.given("New order is created").expects_to_receive("OrderCreated event").with_content(expected_message)
    data = create_proto_from_pact(proto.OrderCreated, expected_message)

    with pact:
        await service.order_created_handler(data, correlation_id=uuid.UUID("23b2c005-a914-41ab-92d7-d8d4d8e98020"))

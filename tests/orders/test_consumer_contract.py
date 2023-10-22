import uuid

import pytest
import pytest_asyncio
from pact import Format, MessageConsumer, MessagePact, Provider, Term

from adapters import proto
from orders.app import Service
from tests.pact_helpers import create_proto_from_pact


@pytest.fixture()
def pact() -> MessagePact:
    return MessageConsumer("service-orders", version="0.0.3").has_pact_with(
        Provider("service-customers"),
        publish_to_broker=True,
        broker_base_url="http://localhost:9292",
        broker_username="pactbroker",
        broker_password="pactbroker",
        pact_dir="pacts",
    )


@pytest_asyncio.fixture()
async def service() -> Service:
    s = Service()
    await s._start_service()
    return s


@pytest.mark.asyncio()
async def test_customer_credit_reserved(pact: MessagePact, service: Service) -> None:
    expected_event = {
        "correlation_id": Term(Format.Regexes.uuid.value, "58b587a2-860c-4c4a-a9af-70457ffae596"),
        "customer_id": Term(Format.Regexes.uuid.value, "1e5df855-a757-4aa5-a55f-2ddf6930b250"),
        "order_id": Term(Format.Regexes.uuid.value, "f408cf27-8c53-486e-89f6-f0b45355b3ed"),
    }
    (
        pact.given("Customer credit is reserved for created order")
        .expects_to_receive("CustomerCreditReserved event")
        .with_content(expected_event)
        .with_metadata({"topic": "customer--credit-reserved"})
    )
    data = create_proto_from_pact(proto.CustomerCreditReserved, expected_event)

    with pact:
        await service.customer_credit_reserved_handler(
            data, correlation_id=uuid.UUID("58b587a2-860c-4c4a-a9af-70457ffae596")
        )

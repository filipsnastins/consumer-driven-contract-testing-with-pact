import uuid
from typing import cast

import pytest
from pact import Format, MessageConsumer, MessagePact, Provider, Term
from pact.matchers import get_generated_values

from orders import proto
from orders.app import ServiceOrders


@pytest.fixture()
def pact() -> MessagePact:
    return MessageConsumer("service-orders", version="0.0.1").has_pact_with(
        Provider("service-customers"),
        publish_to_broker=True,
        broker_base_url="http://localhost:9292",
        broker_username="pactbroker",
        broker_password="pactbroker",
        pact_dir="pacts",
    )


@pytest.fixture()
def service() -> ServiceOrders:
    return ServiceOrders()


@pytest.mark.asyncio()
async def test_customer_credit_reserved(pact: MessagePact, service: ServiceOrders) -> None:
    expected_event = {
        "event_id": Term(Format.Regexes.uuid.value, "be16b759-b0a7-49b3-b754-bbf4596ff092"),
        "correlation_id": Term(Format.Regexes.uuid.value, "58b587a2-860c-4c4a-a9af-70457ffae596"),
        "customer_id": Term(Format.Regexes.uuid.value, "1e5df855-a757-4aa5-a55f-2ddf6930b250"),
        "order_id": Term(Format.Regexes.uuid.value, "f408cf27-8c53-486e-89f6-f0b45355b3ed"),
        "created_at": Term(Format.Regexes.iso_8601_datetime_ms.value, "2023-10-16T13:48:39.917914+00:00"),
    }
    (
        pact.given("Customer credit is reserved for created order")
        .expects_to_receive("CustomerCreditReserved event")
        .with_content(expected_event)
        .with_metadata({"topic": "customer--credit-reserved"})
    )

    with pact:
        generated_values = cast(dict, get_generated_values(expected_event))
        data = proto.CustomerCreditReserved(**generated_values)
        await service.customer_credit_reserved_handler(
            data, correlation_id=uuid.UUID("58b587a2-860c-4c4a-a9af-70457ffae596")
        )

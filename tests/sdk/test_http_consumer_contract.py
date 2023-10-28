import uuid
from decimal import Decimal
from typing import Generator

import pytest
from pact import Consumer, Format, Like, Pact, Provider, Term
from tomodachi_testcontainers.utils import get_available_port
from yarl import URL

from sdk.orders import OrderCreatedResponse, OrdersClient


@pytest.fixture(scope="module")
def mock_url() -> URL:
    return URL(f"http://localhost:{get_available_port()}")


@pytest.fixture(scope="module")
def pact(mock_url: URL) -> Generator[Pact, None, None]:
    consumer = Consumer("sdk--rest", version="0.0.1")
    pact = consumer.has_pact_with(
        Provider("service-orders--rest"),
        pact_dir="pacts",
        publish_to_broker=True,
        broker_base_url="http://localhost:9292",
        broker_username="pactbroker",
        broker_password="pactbroker",
        # Mock service configuration
        host_name=str(mock_url.host),
        port=int(mock_url.port or 80),
    )
    pact.start_service()
    yield pact
    pact.stop_service()


@pytest.fixture(scope="module")
def orders_client(mock_url: URL) -> OrdersClient:
    return OrdersClient(str(mock_url))


@pytest.mark.asyncio()
async def test_create_order(pact: Pact, orders_client: OrdersClient) -> None:
    expected = {
        "order_id": Term(Format.Regexes.uuid.value, "f408cf27-8c53-486e-89f6-f0b45355b3ed"),
        "order_total": Like(10099),
    }

    (
        pact.upon_receiving("A request to create a new order")
        .with_request(
            method="POST",
            path="/order",
            body={
                "customer_id": "f408cf27-8c53-486e-89f6-f0b45355b3ed",
                "order_total": 10099,
            },
        )
        .will_respond_with(status=200, body=expected)
    )

    with pact:
        order = await orders_client.create_order(
            customer_id=uuid.UUID("f408cf27-8c53-486e-89f6-f0b45355b3ed"),
            order_total=Decimal("100.99"),
        )

        assert isinstance(order, OrderCreatedResponse)
        assert order == OrderCreatedResponse(
            order_id=uuid.UUID("f408cf27-8c53-486e-89f6-f0b45355b3ed"),
            order_total=Decimal("100.99"),
        )

        pact.verify()

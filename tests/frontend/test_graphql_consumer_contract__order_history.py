import uuid
from decimal import Decimal
from typing import Generator

import pytest
from pact import Consumer, EachLike, Format, Like, Pact, Provider, Term
from tomodachi_testcontainers.utils import get_available_port
from yarl import URL

from frontend.order_history import Customer, Order, OrderHistoryClient

pytestmark = [pytest.mark.frontend__graphql(), pytest.mark.consumer(), pytest.mark.pactflow(), pytest.mark.order(1)]


@pytest.fixture(scope="module")
def mock_url() -> URL:
    return URL(f"http://localhost:{get_available_port()}")


@pytest.fixture(scope="module")
def pact(mock_url: URL) -> Generator[Pact, None, None]:
    pact = Consumer("frontend--graphql", auto_detect_version_properties=True).has_pact_with(
        Provider("service-order-history--graphql"),
        pact_dir="pacts",
        host_name=str(mock_url.host),
        port=int(mock_url.port or 80),
    )
    pact.start_service()
    yield pact
    pact.stop_service()


@pytest.fixture(scope="module")
def client(mock_url: URL) -> OrderHistoryClient:
    return OrderHistoryClient(str(mock_url))


@pytest.mark.asyncio()
async def test_get_all_customers(pact: Pact, client: OrderHistoryClient) -> None:
    # Arrange
    expected = {
        "data": {
            "getAllCustomers": EachLike(
                {
                    "id": Term(Format.Regexes.uuid.value, "d3100f4f-c8a7-4207-a5e2-40aa122b4b33"),
                    "name": Like("John Doe"),
                    "orders": EachLike(
                        {
                            "id": Term(Format.Regexes.uuid.value, "f408cf27-8c53-486e-89f6-f0b45355b3ed"),
                            "orderTotal": Like(12399),
                            "state": Like("CREATED"),
                        }
                    ),
                }
            )
        }
    }
    (
        pact.given("A customer d3100f4f exists")
        .upon_receiving("A request to get all customers")
        .with_request(
            method="POST",
            path="/graphql",
            headers={"Content-Type": "application/json"},
            body={
                "query": "{getAllCustomers {id name orders {id orderTotal state}}}",
            },
        )
        .will_respond_with(status=200, body=expected)
    )

    # Act & Assert not raised
    with pact:
        customers = await client.get_all_customers()
        assert customers == [
            Customer(
                id=uuid.UUID("d3100f4f-c8a7-4207-a5e2-40aa122b4b33"),
                name="John Doe",
                orders=[
                    Order(
                        id=uuid.UUID("f408cf27-8c53-486e-89f6-f0b45355b3ed"),
                        order_total=Decimal("123.99"),
                        state="CREATED",
                    )
                ],
            )
        ]

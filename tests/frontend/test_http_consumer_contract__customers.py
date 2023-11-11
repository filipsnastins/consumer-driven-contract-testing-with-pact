import uuid
from typing import Generator

import pytest
from pact import Consumer, Format, Like, Pact, Provider, Term
from tomodachi_testcontainers.utils import get_available_port
from yarl import URL

from frontend.customers import Customer, CustomerClient, CustomerNotFoundError

pytestmark = [pytest.mark.frontend(), pytest.mark.consumer(), pytest.mark.pactflow(), pytest.mark.order(1)]


@pytest.fixture(scope="module")
def mock_url() -> URL:
    return URL(f"http://localhost:{get_available_port()}")


@pytest.fixture(scope="module")
def pact(mock_url: URL) -> Generator[Pact, None, None]:
    pact = Consumer("frontend--rest", auto_detect_version_properties=True).has_pact_with(
        Provider("service-customers--rest"),
        pact_dir="pacts",
        host_name=str(mock_url.host),
        port=int(mock_url.port or 80),
    )
    pact.start_service()
    yield pact
    pact.stop_service()


@pytest.fixture(scope="module")
def client(mock_url: URL) -> CustomerClient:
    return CustomerClient(str(mock_url))


@pytest.mark.asyncio()
async def test_create_customer(pact: Pact, client: CustomerClient) -> None:
    # Arrange
    expected = {
        "id": Term(Format.Regexes.uuid.value, "d3100f4f-c8a7-4207-a5e2-40aa122b4b33"),
        "name": Like("John Doe"),
    }
    (
        pact.upon_receiving("A request to create a new customer")
        .with_request(
            method="POST",
            path="/customer",
            headers={"Content-Type": "application/json"},
            body={
                "name": "John Doe",
            },
        )
        .will_respond_with(status=200, body=expected)
    )

    with pact:
        # Act
        order = await client.create(name="John Doe")

        # Assert
        assert isinstance(order, Customer)
        assert order == Customer(
            id=uuid.UUID("d3100f4f-c8a7-4207-a5e2-40aa122b4b33"),
            name="John Doe",
        )
        pact.verify()


@pytest.mark.asyncio()
async def test_get_non_existing_customer(pact: Pact, client: CustomerClient) -> None:
    # Arrange
    expected = {"error": "CUSTOMER_NOT_FOUND"}
    (
        pact.upon_receiving("A request to get non-existing customer")
        .with_request(
            method="GET",
            path="/customer/02f0a114-273d-4e40-af9e-129f8e3c193d",
        )
        .will_respond_with(status=404, body=expected)
    )

    with pact:
        # Act & assert
        with pytest.raises(CustomerNotFoundError):
            await client.get(uuid.UUID("02f0a114-273d-4e40-af9e-129f8e3c193d"))

        pact.verify()


@pytest.mark.asyncio()
async def test_get_customer(pact: Pact, client: CustomerClient) -> None:
    # Arrange
    expected = {
        "id": Term(Format.Regexes.uuid.value, "d3100f4f-c8a7-4207-a5e2-40aa122b4b33"),
        "name": Like("John Doe"),
    }
    (
        pact.given("A customer d3100f4f exists")
        .upon_receiving("A request to get an existing customer")
        .with_request(
            method="GET",
            path="/customer/d3100f4f-c8a7-4207-a5e2-40aa122b4b33",
        )
        .will_respond_with(status=200, body=expected)
    )

    with pact:
        # Act
        order = await client.get(uuid.UUID("d3100f4f-c8a7-4207-a5e2-40aa122b4b33"))

        # Assert
        assert isinstance(order, Customer)
        assert order == Customer(
            id=uuid.UUID("d3100f4f-c8a7-4207-a5e2-40aa122b4b33"),
            name="John Doe",
        )
        pact.verify()

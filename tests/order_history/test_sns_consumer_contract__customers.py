import uuid

import pytest
import pytest_asyncio
from pact import Format, Like, MessageConsumer, MessagePact, Provider, Term
from pytest_mock import MockerFixture

from adapters import proto
from order_history.tomodachi_app import ServiceOrderHistory
from tests.fakes import InMemoryOrderHistoryRepository
from tests.pact_helpers import create_proto_from_pact

pytestmark = [pytest.mark.order_history__sns(), pytest.mark.consumer(), pytest.mark.order(1)]


@pytest.fixture()
def pact() -> MessagePact:
    return MessageConsumer(
        "service-order-history--sns",
        auto_detect_version_properties=True,
    ).has_pact_with(
        Provider("service-customers--sns"),
        pact_dir="pacts",
    )


@pytest.fixture()
def repository() -> InMemoryOrderHistoryRepository:
    return InMemoryOrderHistoryRepository([])


@pytest_asyncio.fixture()
async def service(mocker: MockerFixture, repository: InMemoryOrderHistoryRepository) -> ServiceOrderHistory:
    service = ServiceOrderHistory()
    mocker.patch.object(service, "_repository", repository)
    return service


@pytest.mark.asyncio()
async def test_customer_created(pact: MessagePact, service: ServiceOrderHistory) -> None:
    # Arrange
    expected_message = {
        "customer_id": Term(Format.Regexes.uuid.value, "1e5df855-a757-4aa5-a55f-2ddf6930b250"),
        "name": Like("John Doe"),
    }

    pact.given("New customer is created").expects_to_receive("CustomerCreated event").with_content(expected_message)

    # Act & Assert not raised
    with pact:
        data = create_proto_from_pact(proto.CustomerCreated, expected_message)
        await service.customer_created_handler(data, correlation_id=uuid.UUID("58b587a2-860c-4c4a-a9af-70457ffae596"))

import uuid
from decimal import Decimal

import pytest
import pytest_asyncio
from pact import Format, Like, MessageConsumer, MessagePact, Provider, Term
from pytest_mock import MockerFixture

from adapters import proto
from order_history import use_cases
from order_history.commands import RegisterNewCustomerCommand, RegisterNewOrderCommand
from order_history.tomodachi_app import ServiceOrderHistory
from tests.fakes import InMemoryOrderHistoryRepository
from tests.pact_helpers import create_proto_from_pact

pytestmark = [pytest.mark.consumer(), pytest.mark.order(1)]


@pytest.fixture()
def pact() -> MessagePact:
    return MessageConsumer(
        "service-order-history--sns",
        auto_detect_version_properties=True,
    ).has_pact_with(
        Provider("service-orders--sns"),
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
async def test_order_created(
    pact: MessagePact, service: ServiceOrderHistory, repository: InMemoryOrderHistoryRepository
) -> None:
    await use_cases.register_new_customer(
        RegisterNewCustomerCommand(
            customer_id=uuid.UUID("1e5df855-a757-4aa5-a55f-2ddf6930b250"),
            name="John Doe",
        ),
        repository,
    )

    expected_message = {
        "customer_id": Term(Format.Regexes.uuid.value, "1e5df855-a757-4aa5-a55f-2ddf6930b250"),
        "order_id": Term(Format.Regexes.uuid.value, "f408cf27-8c53-486e-89f6-f0b45355b3ed"),
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
        await service.order_created_handler(data, correlation_id=uuid.UUID("58b587a2-860c-4c4a-a9af-70457ffae596"))


@pytest.mark.asyncio()
async def test_order_approved(
    pact: MessagePact, service: ServiceOrderHistory, repository: InMemoryOrderHistoryRepository
) -> None:
    await use_cases.register_new_customer(
        RegisterNewCustomerCommand(
            customer_id=uuid.UUID("1e5df855-a757-4aa5-a55f-2ddf6930b250"),
            name="John Doe",
        ),
        repository,
    )
    await use_cases.register_new_order(
        RegisterNewOrderCommand(
            customer_id=uuid.UUID("1e5df855-a757-4aa5-a55f-2ddf6930b250"),
            order_id=uuid.UUID("f408cf27-8c53-486e-89f6-f0b45355b3ed"),
            order_total=Decimal("100.99"),
        ),
        repository,
    )

    expected_message = {
        "order_id": Term(Format.Regexes.uuid.value, "f408cf27-8c53-486e-89f6-f0b45355b3ed"),
    }
    (
        pact.given("A created order has been approved")
        .expects_to_receive("OrderApproved event")
        .with_content(expected_message)
    )

    with pact:
        data = create_proto_from_pact(proto.OrderApproved, expected_message)
        await service.order_approved_handler(data, correlation_id=uuid.UUID("58b587a2-860c-4c4a-a9af-70457ffae596"))

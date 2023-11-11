import uuid
from decimal import Decimal

import pytest
import pytest_asyncio
from pact import Format, MessageConsumer, MessagePact, Provider, Term
from pytest_mock import MockerFixture

from adapters import proto
from orders import use_cases
from orders.commands import CreateOrderCommand
from orders.tomodachi_app import ServiceOrders
from tests.fakes import InMemoryMessagePublisher, InMemoryOrderRepository
from tests.pact_helpers import create_proto_from_pact

pytestmark = [pytest.mark.consumer(), pytest.mark.pactflow(), pytest.mark.order(1)]


@pytest.fixture()
def pact() -> MessagePact:
    return MessageConsumer(
        "service-orders--sns",
        auto_detect_version_properties=True,
    ).has_pact_with(
        Provider("service-customers--sns"),
        pact_dir="pacts",
    )


@pytest.fixture()
def repository() -> InMemoryOrderRepository:
    return InMemoryOrderRepository([])


@pytest.fixture()
def publisher() -> InMemoryMessagePublisher:
    return InMemoryMessagePublisher([])


@pytest_asyncio.fixture()
async def service(
    mocker: MockerFixture, repository: InMemoryOrderRepository, publisher: InMemoryMessagePublisher
) -> ServiceOrders:
    service = ServiceOrders()
    mocker.patch.object(service, "_repository", repository)
    mocker.patch.object(service, "_publisher", publisher)
    return service


@pytest.mark.asyncio()
async def test_customer_credit_reserved(
    pact: MessagePact,
    mocker: MockerFixture,
    service: ServiceOrders,
    repository: InMemoryOrderRepository,
    publisher: InMemoryMessagePublisher,
) -> None:
    mocker.patch("orders.domain.uuid.uuid4", return_value=uuid.UUID("f408cf27-8c53-486e-89f6-f0b45355b3ed"))
    order = await use_cases.create_order(
        CreateOrderCommand(
            correlation_id=uuid.UUID("58b587a2-860c-4c4a-a9af-70457ffae596"),
            customer_id=uuid.UUID("1e5df855-a757-4aa5-a55f-2ddf6930b250"),
            order_total=Decimal("123.99"),
        ),
        repository,
        publisher,
    )

    expected_message = {
        "correlation_id": Term(Format.Regexes.uuid.value, "58b587a2-860c-4c4a-a9af-70457ffae596"),
        "customer_id": Term(Format.Regexes.uuid.value, "1e5df855-a757-4aa5-a55f-2ddf6930b250"),
        "order_id": Term(Format.Regexes.uuid.value, str(order.id)),
    }
    (
        pact.given("Customer credit is reserved for created order")
        .expects_to_receive("CustomerCreditReserved event")
        .with_content(expected_message)
    )

    with pact:
        data = create_proto_from_pact(proto.CustomerCreditReserved, expected_message)
        await service.customer_credit_reserved_handler(
            data, correlation_id=uuid.UUID("58b587a2-860c-4c4a-a9af-70457ffae596")
        )

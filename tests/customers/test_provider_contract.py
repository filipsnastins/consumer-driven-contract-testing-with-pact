import uuid
from asyncio import AbstractEventLoop

import pytest_asyncio
from google.protobuf.json_format import MessageToDict
from pact import MessageProvider
from pytest_mock import MockerFixture

from customers import proto
from customers.adapters import MessagePublisher
from customers.app import Service

DEFAULT_OPTS = {
    "broker_url": "http://localhost:9292",
    "broker_username": "pactbroker",
    "broker_password": "pactbroker",
    "publish_verification_results": True,
    "publish_version": "0.0.1",
}


@pytest_asyncio.fixture()
async def service() -> Service:
    s = Service()
    await s._start_service()
    return s


async def customer_credit_reserved_message_provider(service: Service, mocker: MockerFixture) -> dict:
    mock_publisher = mocker.patch.object(service, "_publisher", spec_set=MessagePublisher)

    await service.order_created_handler(
        data=proto.OrderCreated(
            event_id="83ffd100-6d79-40a4-a2fb-22a9d835fa4d92",
            correlation_id="58b587a2-860c-4c4a-a9af-70457ffae596",
            customer_id="1e5df855-a757-4aa5-a55f-2ddf6930b250",
            order_id="f408cf27-8c53-486e-89f6-f0b45355b3ed",
            order_total=12399,
            created_at="2023-10-16T13:48:39.917914+00:00",
        ),
        correlation_id=uuid.UUID("58b587a2-860c-4c4a-a9af-70457ffae596"),
    )

    [call] = mock_publisher.publish.call_args_list
    return MessageToDict(call[0][0], preserving_proto_field_name=True)


def test_verify_service_orders_consumer(event_loop: AbstractEventLoop, service: Service, mocker: MockerFixture) -> None:
    provider = MessageProvider(
        message_providers={
            "Customer credit is reserved for created order": lambda: event_loop.run_until_complete(
                customer_credit_reserved_message_provider(service, mocker)
            ),
        },
        provider="service-customers",
        consumer="service-orders",
        pact_dir="pacts",
    )

    with provider:
        provider.verify_with_broker(**DEFAULT_OPTS)

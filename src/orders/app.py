import uuid

import tomodachi
from aiohttp import web
from stockholm import Money
from tomodachi.envelope.protobuf_base import ProtobufBase

from adapters import clients, dynamodb, proto
from adapters.publisher import AWSSNSSQSMessagePublisher
from orders import use_cases
from orders.commands import ApproveOrderCommand, CreateOrderCommand
from orders.domain import OrderNotFoundError
from orders.events import OrderCreatedEvent
from orders.repository import OrderRepository
from tomodachi_bootstrap import TomodachiServiceBase


class Service(TomodachiServiceBase):
    name = "service--orders"

    def __init__(self) -> None:
        super().__init__()
        self._publisher = AWSSNSSQSMessagePublisher(
            service=self,
            message_topic_map={
                OrderCreatedEvent: "order--created",
            },
        )
        self._repository = OrderRepository(dynamodb.get_table_name(), clients.get_dynamodb_client)

    async def _start_service(self) -> None:
        await dynamodb.create_table()

    @tomodachi.http("POST", r"/order")
    async def create_order_handler(self, request: web.Request, correlation_id: uuid.UUID) -> web.Response:
        body = await request.json()
        cmd = CreateOrderCommand(
            correlation_id=correlation_id,
            customer_id=uuid.UUID(body["customer_id"]),
            order_total=Money.from_sub_units(body["order_total"]).as_decimal(),
        )
        order = await use_cases.create_order(cmd, self._repository, self._publisher)
        return web.json_response(data=order.to_dict())

    @tomodachi.http("GET", r"/order/(?P<order_id>[^/]+?)/?")
    async def get_customer_handler(
        self, request: web.Request, order_id: str, correlation_id: uuid.UUID
    ) -> web.Response:
        try:
            order = await use_cases.get_order(uuid.UUID(order_id), self._repository)
            return web.json_response(order.to_dict(), status=200)
        except OrderNotFoundError:
            return web.json_response({"error": "ORDER_NOT_FOUND"}, status=404)

    @tomodachi.aws_sns_sqs(
        topic="customer--credit-reserved",
        queue_name="orders--customer-credit-reserved",
        dead_letter_queue_name="orders--customer-credit-reserved--dlq",
        max_receive_count=1,
        proto_class=proto.CustomerCreditReserved,
        message_envelope=ProtobufBase,
    )
    async def customer_credit_reserved_handler(
        self, data: proto.CustomerCreditReserved, correlation_id: uuid.UUID
    ) -> None:
        cmd = ApproveOrderCommand(
            order_id=uuid.UUID(data.order_id),
            customer_id=uuid.UUID(data.customer_id),
        )
        await use_cases.approve_order(cmd, self._repository)

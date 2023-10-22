import uuid

import tomodachi
from aiohttp import web
from stockholm import Money
from tomodachi.envelope.protobuf_base import ProtobufBase

from adapters import proto
from adapters.publisher import AWSSNSSQSMessagePublisher
from orders import use_cases
from orders.commands import ApproveOrderCommand, CreateOrderCommand
from orders.events import OrderCreatedEvent
from tomodachi_bootstrap import TomodachiServiceBase


class Service(TomodachiServiceBase):
    name = "service--orders"

    async def _start_service(self) -> None:
        self._publisher = AWSSNSSQSMessagePublisher(
            service=self,
            message_topic_map={
                OrderCreatedEvent: "order--created",
            },
        )

    @tomodachi.http("POST", r"/order")
    async def create_order_handler(self, request: web.Request, correlation_id: uuid.UUID) -> web.Response:
        body = await request.json()
        cmd = CreateOrderCommand(
            correlation_id=correlation_id,
            customer_id=uuid.UUID(body["customer_id"]),
            order_total=Money.from_sub_units(body["order_total"]).as_decimal(),
        )
        response = await use_cases.create_order(cmd, publisher=self._publisher)
        return web.json_response(data=response.to_dict())

    @tomodachi.aws_sns_sqs(
        topic="customer--credit-reserved",
        queue_name="orders--customer-credit-reserved",
        dead_letter_queue_name="orders--customer-credit-reserved--dlq",
        max_receive_count=3,
        proto_class=proto.CustomerCreditReserved,
        message_envelope=ProtobufBase,
    )
    async def customer_credit_reserved_handler(
        self, data: proto.CustomerCreditReserved, correlation_id: uuid.UUID
    ) -> None:
        cmd = ApproveOrderCommand(
            correlation_id=correlation_id,
            order_id=uuid.UUID(data.order_id),
            customer_id=uuid.UUID(data.customer_id),
        )
        await use_cases.approve_order(cmd)

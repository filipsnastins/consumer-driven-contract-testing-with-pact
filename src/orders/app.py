import uuid

import structlog
import tomodachi
from aiohttp import web
from stockholm import Money
from tomodachi.envelope.protobuf_base import ProtobufBase

from orders import adapters, proto, use_cases
from orders.commands import ApproveOrderCommand, CreateOrderCommand
from tomodachi_bootstrap import TomodachiServiceBase

logger: structlog.stdlib.BoundLogger = structlog.get_logger()


class ServiceOrders(TomodachiServiceBase):
    name = "service--orders"

    async def _start_service(self) -> None:
        self._publisher = adapters.MessagePublisher(self)

    @tomodachi.http("POST", r"/orders")
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
        )
        await use_cases.approve_order(cmd)

import uuid

import tomodachi
from aiohttp import web
from stockholm import Money
from tomodachi.envelope.protobuf_base import ProtobufBase

from adapters import clients, dynamodb, proto
from adapters.publisher import AWSSNSSQSMessagePublisher
from customers import use_cases
from customers.commands import CreateCustomerCommand, ReserveCustomerCreditCommand
from customers.domain import CustomerNotFoundError
from customers.events import CustomerCreditReservedEvent
from customers.repository import DynamoDBCustomerRepository
from tomodachi_bootstrap import TomodachiServiceBase


class Service(TomodachiServiceBase):
    name = "service--customers"

    def __init__(self) -> None:
        super().__init__()
        self._publisher = AWSSNSSQSMessagePublisher(
            service=self,
            message_topic_map={
                CustomerCreditReservedEvent: "customer--credit-reserved",
            },
        )
        self._repository = DynamoDBCustomerRepository(dynamodb.get_table_name(), clients.get_dynamodb_client)

    async def _start_service(self) -> None:
        await dynamodb.create_table()

    @tomodachi.http("POST", r"/customer")
    async def create_customer_handler(self, request: web.Request, correlation_id: uuid.UUID) -> web.Response:
        data = await request.json()
        cmd = CreateCustomerCommand(name=str(data["name"]))
        customer = await use_cases.create_customer(cmd, self._repository)
        return web.json_response(customer.to_dict(), status=200)

    @tomodachi.http("GET", r"/customer/(?P<customer_id>[^/]+?)/?")
    async def get_customer_handler(
        self, request: web.Request, customer_id: str, correlation_id: uuid.UUID
    ) -> web.Response:
        try:
            customer = await use_cases.get_customer(uuid.UUID(customer_id), self._repository)
            return web.json_response(customer.to_dict(), status=200)
        except CustomerNotFoundError:
            return web.json_response({"error": "CUSTOMER_NOT_FOUND"}, status=404)

    @tomodachi.aws_sns_sqs(
        topic="order--created",
        queue_name="customers--order-created",
        dead_letter_queue_name="customers--order-created--dlq",
        max_receive_count=1,
        proto_class=proto.OrderCreated,
        message_envelope=ProtobufBase,
    )
    async def order_created_handler(self, data: proto.OrderCreated, correlation_id: uuid.UUID) -> None:
        cmd = ReserveCustomerCreditCommand(
            customer_id=uuid.UUID(data.customer_id),
            order_id=uuid.UUID(data.order_id),
            order_total=Money.from_proto(data.order_total).as_decimal(),
        )
        await use_cases.reserve_customer_credit(cmd, self._repository, self._publisher)

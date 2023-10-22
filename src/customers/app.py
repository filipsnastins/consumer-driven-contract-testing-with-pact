import uuid

import tomodachi
from stockholm import Money
from tomodachi.envelope.protobuf_base import ProtobufBase

from adapters import proto
from adapters.publisher import AWSSNSSQSMessagePublisher
from customers import use_cases
from customers.commands import ReserveCustomerCreditCommand
from customers.events import CustomerCreditReservedEvent
from tomodachi_bootstrap import TomodachiServiceBase


class Service(TomodachiServiceBase):
    name = "service--customers"

    async def _start_service(self) -> None:
        self._publisher = AWSSNSSQSMessagePublisher(
            service=self,
            message_topic_map={
                CustomerCreditReservedEvent: "customer--credit-reserved",
            },
        )

    @tomodachi.aws_sns_sqs(
        topic="order--created",
        queue_name="customers--order-created",
        dead_letter_queue_name="customers--order-created--dlq",
        max_receive_count=3,
        proto_class=proto.OrderCreated,
        message_envelope=ProtobufBase,
    )
    async def order_created_handler(self, data: proto.OrderCreated, correlation_id: uuid.UUID) -> None:
        cmd = ReserveCustomerCreditCommand(
            correlation_id=correlation_id,
            customer_id=uuid.UUID(data.customer_id),
            order_id=uuid.UUID(data.order_id),
            order_total=Money.from_sub_units(data.order_total).as_decimal(),
        )
        await use_cases.reserve_customer_credit(cmd, publisher=self._publisher)

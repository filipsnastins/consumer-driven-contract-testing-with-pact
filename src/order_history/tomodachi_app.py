import uuid

import structlog
import tomodachi
from stockholm import Money
from tomodachi.envelope.protobuf_base import ProtobufBase

from adapters import proto, sqlalchemy
from order_history import use_cases
from order_history.commands import RegisterNewCustomerCommand, RegisterNewOrderCommand, RegisterOrderApprovedCommand
from order_history.repository import Base, SQLAlchemyOrderHistoryRepository
from service_layer.tomodachi_bootstrap import TomodachiServiceBase

logger: structlog.stdlib.BoundLogger = structlog.get_logger()


class ServiceOrderHistory(TomodachiServiceBase):
    name = "service--order-history"

    def __init__(self) -> None:
        super().__init__()
        self._repository = SQLAlchemyOrderHistoryRepository(sqlalchemy.session_factory)

    async def _start_service(self) -> None:
        async with sqlalchemy.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("database_created")

    @tomodachi.aws_sns_sqs(
        topic="customer--created",
        queue_name="order-history--customer-created",
        dead_letter_queue_name="order-history--customer-created--dlq",
        max_receive_count=1,
        proto_class=proto.CustomerCreated,
        message_envelope=ProtobufBase,
    )
    async def customer_created_handler(self, data: proto.CustomerCreated, correlation_id: uuid.UUID) -> None:
        cmd = RegisterNewCustomerCommand(customer_id=uuid.UUID(data.customer_id), name=data.name)
        await use_cases.register_new_customer(cmd, self._repository)

    @tomodachi.aws_sns_sqs(
        topic="order--created",
        queue_name="order-history--order-created",
        dead_letter_queue_name="order-history--order-created--dlq",
        max_receive_count=1,
        proto_class=proto.OrderCreated,
        message_envelope=ProtobufBase,
    )
    async def order_created_handler(self, data: proto.OrderCreated, correlation_id: uuid.UUID) -> None:
        cmd = RegisterNewOrderCommand(
            customer_id=uuid.UUID(data.customer_id),
            order_id=uuid.UUID(data.order_id),
            order_total=Money.from_proto(data.order_total).as_decimal(),
        )
        await use_cases.register_new_order(cmd, self._repository)

    @tomodachi.aws_sns_sqs(
        topic="order--approved",
        queue_name="order-history--order-approved",
        dead_letter_queue_name="order-history--order-approved--dlq",
        max_receive_count=1,
        proto_class=proto.OrderApproved,
        message_envelope=ProtobufBase,
    )
    async def order_approved_handler(self, data: proto.OrderApproved, correlation_id: uuid.UUID) -> None:
        cmd = RegisterOrderApprovedCommand(order_id=uuid.UUID(data.order_id))
        await use_cases.register_order_approved(cmd, self._repository)

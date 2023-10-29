import uuid

import structlog
import tomodachi
from tomodachi.envelope.protobuf_base import ProtobufBase

from adapters import proto
from service_layer.tomodachi_bootstrap import TomodachiServiceBase

logger: structlog.stdlib.BoundLogger = structlog.get_logger()


class ServiceOrderHistory(TomodachiServiceBase):
    name = "service--order-history"

    @tomodachi.aws_sns_sqs(
        topic="customer--created",
        queue_name="order-history--customer-created",
        dead_letter_queue_name="order-history--customer-created--dlq",
        max_receive_count=1,
        proto_class=proto.CustomerCreated,
        message_envelope=ProtobufBase,
    )
    async def customer_created_handler(self, data: proto.CustomerCreated, correlation_id: uuid.UUID) -> None:
        logger.info("customer_created", customer_id=data.customer_id, correlation_id=correlation_id)

    @tomodachi.aws_sns_sqs(
        topic="order--created",
        queue_name="order-history--order-created",
        dead_letter_queue_name="order-history--order-created--dlq",
        max_receive_count=1,
        proto_class=proto.OrderCreated,
        message_envelope=ProtobufBase,
    )
    async def order_created_handler(self, data: proto.OrderCreated, correlation_id: uuid.UUID) -> None:
        logger.info(
            "order_created", order_id=data.order_id, customer_id=data.customer_id, correlation_id=correlation_id
        )

    @tomodachi.aws_sns_sqs(
        topic="order--approved",
        queue_name="order-history--order-approved",
        dead_letter_queue_name="order-history--order-approved--dlq",
        max_receive_count=1,
        proto_class=proto.OrderApproved,
        message_envelope=ProtobufBase,
    )
    async def order_approved_handler(self, data: proto.OrderApproved, correlation_id: uuid.UUID) -> None:
        logger.info(
            "order_approved", order_id=data.order_id, customer_id=data.customer_id, correlation_id=correlation_id
        )

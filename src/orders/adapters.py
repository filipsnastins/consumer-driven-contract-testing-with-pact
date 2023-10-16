import structlog
import tomodachi
from tomodachi.envelope.protobuf_base import ProtobufBase

from orders.events import Event

logger: structlog.stdlib.BoundLogger = structlog.get_logger()


class MessagePublisher:
    def __init__(self, service: tomodachi.Service) -> None:
        self._service = service

    async def publish(self, event: Event, topic: str) -> None:
        data = event.to_proto()
        await tomodachi.aws_sns_sqs_publish(
            service=self._service,
            data=data,
            topic=topic,
            message_envelope=ProtobufBase,
        )
        logger.info(
            "message_published",
            topic=topic,
            message_type=data.DESCRIPTOR.full_name,
        )

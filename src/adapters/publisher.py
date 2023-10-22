from typing import Protocol

import structlog
import tomodachi
from google.protobuf.message import Message as ProtoMessage
from tomodachi.envelope.protobuf_base import ProtobufBase

logger: structlog.stdlib.BoundLogger = structlog.get_logger()


class Message(Protocol):
    def to_proto(self) -> ProtoMessage:
        ...


class MessagePublisher(Protocol):
    async def publish(self, message: Message) -> None:
        ...


class AWSSNSSQSMessagePublisher:
    def __init__(self, service: tomodachi.Service, message_topic_map: dict[type[Message], str]) -> None:
        self._service = service
        self._message_topic_map = message_topic_map

    async def publish(self, message: Message) -> None:
        topic = self._message_topic_map[type(message)]
        data = message.to_proto()
        await tomodachi.aws_sns_sqs_publish(
            service=self._service,
            data=data,
            topic=topic,
            message_envelope=ProtobufBase,
        )
        logger.info(
            "message_published",
            topic=topic,
            message_type=type(message),
            proto_data_type=data.DESCRIPTOR.full_name,
        )

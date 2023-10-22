from google.protobuf.message import Message

from adapters.publisher import MessagePublisher


class InMemoryMessagePublisher(MessagePublisher):
    def __init__(self, messages: list[Message]) -> None:
        self.messages = messages

    async def publish(self, data: Message, topic: str) -> None:
        self.messages.append(data)

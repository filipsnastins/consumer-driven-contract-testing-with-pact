from adapters.publisher import Message, MessagePublisher


class InMemoryMessagePublisher(MessagePublisher):
    def __init__(self, messages: list[Message]) -> None:
        self.messages = messages

    async def publish(self, message: Message) -> None:
        self.messages.append(message)

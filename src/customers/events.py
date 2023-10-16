import datetime
import uuid
from dataclasses import dataclass
from typing import Protocol

from google.protobuf.message import Message

from customers import proto


class Event(Protocol):
    event_id: uuid.UUID
    correlation_id: uuid.UUID
    order_id: uuid.UUID
    created_at: datetime.datetime

    def to_proto(self) -> Message:
        ...


@dataclass
class CustomerCreditReservedEvent:
    event_id: uuid.UUID
    correlation_id: uuid.UUID
    order_id: uuid.UUID
    customer_id: uuid.UUID
    created_at: datetime.datetime

    def to_proto(self) -> proto.CustomerCreditReserved:
        return proto.CustomerCreditReserved(
            event_id=str(self.event_id),
            correlation_id=str(self.correlation_id),
            customer_id=str(self.customer_id),
            order_id=str(self.order_id),
            created_at=self.created_at.isoformat(),
        )

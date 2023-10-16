import datetime
import uuid
from dataclasses import dataclass
from decimal import Decimal
from typing import Protocol

from google.protobuf.message import Message
from stockholm import Money

from proto.order_created.v1 import order_created_pb2


class Event(Protocol):
    event_id: uuid.UUID
    correlation_id: uuid.UUID
    order_id: uuid.UUID
    created_at: datetime.datetime

    def to_proto(self) -> Message:
        ...


@dataclass()
class OrderCreatedEvent(Event):
    event_id: uuid.UUID
    correlation_id: uuid.UUID
    order_id: uuid.UUID
    customer_id: uuid.UUID
    order_total: Decimal
    created_at: datetime.datetime

    def to_proto(self) -> order_created_pb2.OrderCreated:
        return order_created_pb2.OrderCreated(
            event_id=str(self.event_id),
            correlation_id=str(self.correlation_id),
            customer_id=str(self.customer_id),
            order_id=str(self.order_id),
            order_total=int(Money(self.order_total).to_sub_units()),
            created_at=self.created_at.isoformat(),
        )

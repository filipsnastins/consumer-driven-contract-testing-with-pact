import datetime
import uuid
from dataclasses import dataclass
from decimal import Decimal
from typing import Protocol

from google.protobuf.message import Message as ProtoMessage
from stockholm import Money

from adapters import proto


class Event(Protocol):
    event_id: uuid.UUID
    correlation_id: uuid.UUID
    order_id: uuid.UUID
    created_at: datetime.datetime

    def to_proto(self) -> ProtoMessage:
        ...


@dataclass
class OrderCreatedEvent:
    event_id: uuid.UUID
    correlation_id: uuid.UUID
    order_id: uuid.UUID
    customer_id: uuid.UUID
    order_total: Decimal
    created_at: datetime.datetime

    def to_proto(self) -> proto.OrderCreated:
        return proto.OrderCreated(
            event_id=str(self.event_id),
            correlation_id=str(self.correlation_id),
            customer_id=str(self.customer_id),
            order_id=str(self.order_id),
            order_total=int(Money(self.order_total).to_sub_units()),
            created_at=self.created_at.isoformat(),
        )

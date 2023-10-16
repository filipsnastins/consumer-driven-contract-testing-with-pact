import datetime
import uuid
from dataclasses import dataclass
from decimal import Decimal

from orders.events import OrderCreatedEvent


@dataclass
class Order:
    order_id: uuid.UUID
    customer_id: uuid.UUID
    order_total: Decimal
    created_at: datetime.datetime

    @staticmethod
    def create(
        correlation_id: uuid.UUID,
        customer_id: uuid.UUID,
        order_total: Decimal,
    ) -> tuple["Order", OrderCreatedEvent]:
        order = Order(
            order_id=uuid.uuid4(),
            customer_id=customer_id,
            order_total=order_total,
            created_at=datetime.datetime.now().replace(tzinfo=datetime.UTC),
        )
        event = OrderCreatedEvent(
            event_id=uuid.uuid4(),
            correlation_id=correlation_id,
            customer_id=order.customer_id,
            order_id=order.order_id,
            order_total=order.order_total,
            created_at=order.created_at,
        )
        return order, event

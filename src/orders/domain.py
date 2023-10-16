import datetime
import uuid
from decimal import Decimal
from enum import Enum

from orders.events import OrderCreatedEvent


class OrderState(Enum):
    CREATED = "CREATED"
    APPROVED = "APPROVED"


class Order:
    def __init__(
        self,
        order_id: uuid.UUID,
        customer_id: uuid.UUID,
        order_total: Decimal,
        state: OrderState,
    ) -> None:
        self.order_id = order_id
        self.customer_id = customer_id
        self.order_total = order_total
        self.state = state

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
            state=OrderState.CREATED,
        )
        event = OrderCreatedEvent(
            event_id=uuid.uuid4(),
            correlation_id=correlation_id,
            customer_id=order.customer_id,
            order_id=order.order_id,
            order_total=order.order_total,
            created_at=datetime.datetime.now().replace(tzinfo=datetime.UTC),
        )
        return order, event

    def approve(self) -> None:
        self.state = OrderState.APPROVED

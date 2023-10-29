import datetime
import uuid
from decimal import Decimal
from enum import Enum

from stockholm import Money

from orders.events import OrderApprovedEvent, OrderCreatedEvent


class OrderNotFoundError(Exception):
    pass


class OrderState(Enum):
    CREATED = "CREATED"
    APPROVED = "APPROVED"


class Order:
    def __init__(
        self,
        id: uuid.UUID,
        customer_id: uuid.UUID,
        order_total: Decimal,
        state: OrderState,
    ) -> None:
        self.id = id
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
            id=uuid.uuid4(),
            customer_id=customer_id,
            order_total=order_total,
            state=OrderState.CREATED,
        )
        event = OrderCreatedEvent(
            event_id=uuid.uuid4(),
            correlation_id=correlation_id,
            customer_id=order.customer_id,
            order_id=order.id,
            order_total=order.order_total,
            created_at=datetime.datetime.now().replace(tzinfo=datetime.UTC),
        )
        return order, event

    def approve(self, correlation_id: uuid.UUID) -> OrderApprovedEvent:
        self.state = OrderState.APPROVED
        return OrderApprovedEvent(
            event_id=uuid.uuid4(),
            correlation_id=correlation_id,
            order_id=self.id,
            customer_id=self.customer_id,
            created_at=datetime.datetime.now().replace(tzinfo=datetime.UTC),
        )

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "customer_id": str(self.customer_id),
            "order_total": int(Money(self.order_total).to_sub_units()),
            "state": self.state.value,
        }

import datetime
import uuid
from dataclasses import dataclass
from decimal import Decimal

from stockholm import Money

from orders.domain import Order


@dataclass
class CreateOrderResponse:
    order_id: uuid.UUID
    customer_id: uuid.UUID
    order_total: Decimal
    created_at: datetime.datetime

    @staticmethod
    def from_order(order: Order) -> "CreateOrderResponse":
        return CreateOrderResponse(
            order_id=order.order_id,
            customer_id=order.customer_id,
            order_total=order.order_total,
            created_at=datetime.datetime.now().replace(tzinfo=datetime.UTC),
        )

    def to_dict(self) -> dict[str, str | int]:
        return {
            "order_id": str(self.order_id),
            "customer_id": str(self.customer_id),
            "order_total": int(Money(self.order_total).to_sub_units()),
            "created_at": self.created_at.isoformat(),
        }

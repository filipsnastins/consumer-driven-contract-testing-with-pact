import datetime
import uuid
from decimal import Decimal

from customers.events import CustomerCreditReservedEvent


class Customer:
    def __init__(self, customer_id: uuid.UUID) -> None:
        self.customer_id = customer_id
        self.credit_reservations: dict[uuid.UUID, Decimal] = {}

    def reserve_credit(self, order_id: uuid.UUID, order_total: Decimal) -> CustomerCreditReservedEvent:
        self.credit_reservations[order_id] = order_total
        return CustomerCreditReservedEvent(
            event_id=uuid.uuid4(),
            correlation_id=uuid.uuid4(),
            customer_id=self.customer_id,
            order_id=order_id,
            created_at=datetime.datetime.now().replace(tzinfo=datetime.UTC),
        )

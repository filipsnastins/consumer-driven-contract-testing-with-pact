import datetime
import uuid
from decimal import Decimal

from customers.events import CustomerCreditReservedEvent


class CustomerNotFoundError(Exception):
    pass


class Customer:
    def __init__(self, id: uuid.UUID, name: str, credit_reservations: dict[uuid.UUID, Decimal]) -> None:
        self.id = id
        self.name = name
        self.credit_reservations = credit_reservations

    @classmethod
    def create(cls, name: str) -> "Customer":
        return Customer(
            id=uuid.uuid4(),
            name=name,
            credit_reservations={},
        )

    def reserve_credit(self, order_id: uuid.UUID, order_total: Decimal) -> CustomerCreditReservedEvent:
        self.credit_reservations[order_id] = order_total
        return CustomerCreditReservedEvent(
            event_id=uuid.uuid4(),
            correlation_id=uuid.uuid4(),
            customer_id=self.id,
            order_id=order_id,
            created_at=datetime.datetime.now().replace(tzinfo=datetime.UTC),
        )

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "name": self.name,
            "credit_reservations": {
                str(order_id): str(order_total) for order_id, order_total in self.credit_reservations.items()
            },
        }

import uuid
from dataclasses import dataclass
from decimal import Decimal


@dataclass
class ReserveCustomerCreditCommand:
    customer_id: uuid.UUID
    order_id: uuid.UUID
    order_total: Decimal


@dataclass
class CreateCustomerCommand:
    name: str

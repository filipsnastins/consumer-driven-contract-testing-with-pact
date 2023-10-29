import uuid
from dataclasses import dataclass
from decimal import Decimal


@dataclass
class ReserveCustomerCreditCommand:
    correlation_id: uuid.UUID
    customer_id: uuid.UUID
    order_id: uuid.UUID
    order_total: Decimal


@dataclass
class CreateCustomerCommand:
    correlation_id: uuid.UUID
    name: str

import uuid
from dataclasses import dataclass
from decimal import Decimal


@dataclass
class RegisterNewCustomerCommand:
    customer_id: uuid.UUID
    name: str


@dataclass
class RegisterNewOrderCommand:
    customer_id: uuid.UUID
    order_id: uuid.UUID
    order_total: Decimal


@dataclass
class RegisterOrderApprovedCommand:
    order_id: uuid.UUID

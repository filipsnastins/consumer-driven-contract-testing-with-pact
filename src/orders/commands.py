import uuid
from dataclasses import dataclass
from decimal import Decimal


@dataclass
class CreateOrderCommand:
    correlation_id: uuid.UUID
    customer_id: uuid.UUID
    order_total: Decimal


@dataclass
class ApproveOrderCommand:
    correlation_id: uuid.UUID
    order_id: uuid.UUID

import uuid
from dataclasses import dataclass
from decimal import Decimal
from typing import Protocol


class Command(Protocol):
    correlation_id: uuid.UUID


@dataclass
class CreateOrderCommand(Command):
    correlation_id: uuid.UUID
    customer_id: uuid.UUID
    order_total: Decimal

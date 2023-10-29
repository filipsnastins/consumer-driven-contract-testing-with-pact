import uuid
from dataclasses import dataclass
from decimal import Decimal


class OrderNotFoundError(Exception):
    pass


@dataclass
class Customer:
    id: uuid.UUID
    name: str
    orders: list["Order"]


@dataclass
class Order:
    id: uuid.UUID
    state: str
    order_total: Decimal

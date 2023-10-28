import uuid

from adapters.publisher import Message
from customers.domain import Customer
from orders.domain import Order


class InMemoryCustomerRepository:
    def __init__(self, customers: list[Customer]) -> None:
        self.customers = {customer.id: customer for customer in customers}

    async def save(self, customer: Customer) -> None:
        self.customers[customer.id] = customer

    async def get(self, customer_id: uuid.UUID) -> Customer | None:
        return self.customers.get(customer_id)


class InMemoryOrderRepository:
    def __init__(self, orders: list[Order]) -> None:
        self.orders = {order.id: order for order in orders}

    async def save(self, order: Order) -> None:
        self.orders[order.id] = order

    async def get(self, order_id: uuid.UUID) -> Order | None:
        return self.orders.get(order_id)


class InMemoryMessagePublisher:
    def __init__(self, messages: list[Message]) -> None:
        self.messages = messages

    async def publish(self, message: Message) -> None:
        self.messages.append(message)

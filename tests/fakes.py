import uuid
from decimal import Decimal

import customers.domain
import order_history.repository
import orders.domain
from adapters.publisher import Message


class InMemoryCustomerRepository:
    def __init__(self, customers: list[customers.domain.Customer]) -> None:
        self.customers = {customer.id: customer for customer in customers}

    async def save(self, customer: customers.domain.Customer) -> None:
        self.customers[customer.id] = customer

    async def get(self, customer_id: uuid.UUID) -> customers.domain.Customer | None:
        return self.customers.get(customer_id)


class InMemoryOrderRepository:
    def __init__(self, orders: list[orders.domain.Order]) -> None:
        self.orders = {order.id: order for order in orders}

    async def save(self, order: orders.domain.Order) -> None:
        self.orders[order.id] = order

    async def get(self, order_id: uuid.UUID) -> orders.domain.Order | None:
        return self.orders.get(order_id)


class InMemoryOrderHistoryRepository:
    def __init__(self, customers: list[order_history.repository.Customer]) -> None:
        self.customers = {customer.id: customer for customer in customers}

    async def register_new_customer(self, customer_id: uuid.UUID, name: str) -> None:
        self.customers[customer_id] = order_history.repository.Customer(id=customer_id, name=name, orders=[])

    async def register_new_order(
        self, customer_id: uuid.UUID, order_id: uuid.UUID, state: str, order_total: Decimal
    ) -> None:
        order = order_history.repository.Order(
            id=order_id,
            state=state,
            order_total=order_total,
        )
        self.customers[customer_id].orders.append(order)

    async def update_order_state(self, order_id: uuid.UUID, state: str) -> None:
        order = next(order for customer in self.customers.values() for order in customer.orders if order.id == order_id)
        if not order:
            raise order_history.repository.OrderNotFoundError(order_id)
        order.state = state

    async def get_all_customers(self) -> list[order_history.repository.Customer]:
        return list(self.customers.values())


class InMemoryMessagePublisher:
    def __init__(self, messages: list[Message]) -> None:
        self.messages = messages

    async def publish(self, message: Message) -> None:
        self.messages.append(message)

    def clear(self) -> None:
        self.messages.clear()

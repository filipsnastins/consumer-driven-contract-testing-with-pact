import uuid
from decimal import Decimal
from typing import Protocol

from sqlalchemy import UUID, Column, ForeignKey, Integer, String, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, relationship
from stockholm import Money


class OrderNotFoundError(Exception):
    pass


class Base(DeclarativeBase):
    pass


class Customer(Base):
    __tablename__ = "customers"

    id = Column(UUID, primary_key=True, index=True)
    name = Column(String)

    orders: Mapped[list["Order"]] = relationship("Order", back_populates="customer", lazy="joined")


class Order(Base):
    __tablename__ = "orders"

    id = Column(UUID, primary_key=True, index=True)
    customer_id = Column(UUID, ForeignKey("customers.id"))
    state = Column(String)
    order_total = Column(Integer)

    customer: Mapped[Customer] = relationship("Customer", back_populates="orders", lazy="joined")


class OrderHistoryRepository(Protocol):
    async def register_new_customer(self, customer_id: uuid.UUID, name: str) -> None:
        ...

    async def register_new_order(
        self, customer_id: uuid.UUID, order_id: uuid.UUID, state: str, order_total: Decimal
    ) -> None:
        ...

    async def update_order_state(self, order_id: uuid.UUID, state: str) -> None:
        ...

    async def get_all_customers(self) -> list[Customer]:
        ...

    async def get_customer(self, customer_id: uuid.UUID) -> Customer | None:
        ...


class SQLAlchemyOrderHistoryRepository:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def register_new_customer(self, customer_id: uuid.UUID, name: str) -> None:
        async with self._session_factory() as session:
            customer = Customer(
                id=customer_id,
                name=name,
            )
            session.add(customer)
            await session.commit()

    async def register_new_order(
        self, customer_id: uuid.UUID, order_id: uuid.UUID, state: str, order_total: Decimal
    ) -> None:
        async with self._session_factory() as session:
            order = Order(
                id=order_id,
                customer_id=customer_id,
                state=state,
                order_total=int(Money(order_total).to_sub_units()),
            )
            session.add(order)
            await session.commit()

    async def update_order_state(self, order_id: uuid.UUID, state: str) -> None:
        async with self._session_factory() as session:
            stmt = select(Order).where(Order.id == order_id)
            order = await session.scalar(stmt)
            if not order:
                raise OrderNotFoundError(order_id)
            order.state = state
            session.add(order)
            await session.commit()

    async def get_all_customers(self) -> list[Customer]:
        async with self._session_factory() as session:
            stmt = select(Customer)
            return list((await session.scalars(stmt.order_by(Customer.id))).unique())

    async def get_customer(self, customer_id: uuid.UUID) -> Customer | None:
        async with self._session_factory() as session:
            stmt = select(Customer).where(Customer.id == customer_id)
            return await session.scalar(stmt)

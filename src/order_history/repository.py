import uuid
from decimal import Decimal
from typing import Protocol

from sqlalchemy import ForeignKey, Integer, String, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from stockholm import Money

from order_history.domain import Customer, Order, OrderNotFoundError


class Base(DeclarativeBase):
    pass


class CustomerModel(Base):
    __tablename__ = "customers"

    id: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String)

    # FIXME: Async FastAPI and async SQLAlchemy lazy loading didn't work together, so used "joined" eager loading instead
    # Not to be used like this in production
    orders: Mapped[list["OrderModel"]] = relationship("OrderModel", back_populates="customer", lazy="joined")


class OrderModel(Base):
    __tablename__ = "orders"

    id: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    customer_id: Mapped[str] = mapped_column(String, ForeignKey("customers.id"))
    state: Mapped[str] = mapped_column(String)
    order_total: Mapped[Integer] = mapped_column(Integer)

    customer: Mapped[CustomerModel] = relationship("CustomerModel", back_populates="orders", lazy="joined")


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


# FIXME: The repository implementation doesn't handle race conditions, not for production use
class SQLAlchemyOrderHistoryRepository:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def register_new_customer(self, customer_id: uuid.UUID, name: str) -> None:
        async with self._session_factory() as session:
            customer_model = CustomerModel(
                id=str(customer_id),
                name=name,
            )
            session.add(customer_model)
            await session.commit()

    async def register_new_order(
        self, customer_id: uuid.UUID, order_id: uuid.UUID, state: str, order_total: Decimal
    ) -> None:
        async with self._session_factory() as session:
            order_model = OrderModel(
                id=str(order_id),
                customer_id=str(customer_id),
                state=state,
                order_total=int(Money(order_total).to_sub_units()),
            )
            session.add(order_model)
            await session.commit()

    async def update_order_state(self, order_id: uuid.UUID, state: str) -> None:
        async with self._session_factory() as session:
            stmt = select(OrderModel).where(OrderModel.id == str(order_id))
            order_model = await session.scalar(stmt)
            if not order_model:
                raise OrderNotFoundError(order_id)
            order_model.state = state
            session.add(order_model)
            await session.commit()

    async def get_all_customers(self) -> list[Customer]:
        async with self._session_factory() as session:
            stmt = select(CustomerModel)
            customer_models = list((await session.scalars(stmt.order_by(CustomerModel.id))).unique())
            return [
                Customer(
                    id=uuid.UUID(customer_model.id),
                    name=customer_model.name,
                    orders=[
                        Order(
                            id=uuid.UUID(order_model.id),
                            state=order_model.state,
                            order_total=Money.from_sub_units(order_model.order_total).as_decimal(),
                        )
                        for order_model in customer_model.orders
                    ],
                )
                for customer_model in customer_models
            ]

from sqlalchemy import UUID, Column, ForeignKey, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, relationship


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
    order_total = Column(Integer)
    state = Column(String)

    customer: Mapped[Customer] = relationship("Customer", back_populates="orders", lazy="joined")

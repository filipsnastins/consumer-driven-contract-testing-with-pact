import strawberry


@strawberry.type
class OrderType:
    id: str
    order_total: int
    state: str


@strawberry.type
class CustomerType:
    id: str
    name: str
    orders: list[OrderType] | None

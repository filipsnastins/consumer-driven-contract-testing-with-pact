import strawberry


@strawberry.type
class OrderType:
    id: str
    state: str
    order_total: int


@strawberry.type
class CustomerType:
    id: str
    name: str
    orders: list[OrderType]

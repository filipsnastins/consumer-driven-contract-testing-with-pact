import uuid

import structlog
import tomodachi
from aiohttp import web
from stockholm import Money

from orders import adapters, use_cases
from orders.commands import CreateOrderCommand
from tomodachi_bootstrap import TomodachiServiceBase

logger: structlog.stdlib.BoundLogger = structlog.get_logger()


class TomodachiServiceOrders(TomodachiServiceBase):
    name = "service--orders"

    async def _start_service(self) -> None:
        self._publisher = adapters.MessagePublisher(self)

    @tomodachi.http("POST", r"/orders")
    async def create_order(self, request: web.Request, correlation_id: uuid.UUID) -> web.Response:
        body = await request.json()
        cmd = CreateOrderCommand(
            correlation_id=correlation_id,
            customer_id=uuid.UUID(body["customer_id"]),
            order_total=Money.from_sub_units(body["order_total"]).as_decimal(),
        )
        response = await use_cases.create_order(cmd, publisher=self._publisher)
        return web.json_response(data=response.to_dict())

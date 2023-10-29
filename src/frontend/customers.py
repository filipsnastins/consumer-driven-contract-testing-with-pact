import uuid
from dataclasses import dataclass

import httpx


class CustomerNotFoundError(Exception):
    pass


@dataclass
class Customer:
    id: uuid.UUID
    name: str


class CustomerClient:
    def __init__(self, base_url: str) -> None:
        self._client = httpx.AsyncClient(base_url=base_url)

    async def create(self, name: str) -> Customer:
        response = await self._client.post(
            "/customer",
            json={
                "name": name,
            },
        )
        response.raise_for_status()
        body = response.json()
        return Customer(
            id=uuid.UUID(body["id"]),
            name=body["name"],
        )

    async def get(self, customer_id: uuid.UUID) -> Customer:
        response = await self._client.get(f"/customer/{customer_id}")
        if response.status_code == 404:
            raise CustomerNotFoundError(customer_id)
        response.raise_for_status()
        body = response.json()
        return Customer(
            id=uuid.UUID(body["id"]),
            name=body["name"],
        )

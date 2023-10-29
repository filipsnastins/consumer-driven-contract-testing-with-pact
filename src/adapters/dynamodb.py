from typing import Callable

import structlog
from aiobotocore.session import AioSession, get_session
from pydantic import BaseModel
from types_aiobotocore_dynamodb import DynamoDBClient

from adapters.settings import get_tomodachi_app_settings

logger: structlog.stdlib.BoundLogger = structlog.get_logger()

DynamoDBClientFactory = Callable[[], DynamoDBClient]

session: AioSession = get_session()


class AWSClientConfig(BaseModel):
    region_name: str
    aws_access_key_id: str | None = None
    aws_secret_access_key: str | None = None
    endpoint_url: str | None = None

    @staticmethod
    def from_settings() -> "AWSClientConfig":
        settings = get_tomodachi_app_settings()
        return AWSClientConfig(
            region_name=settings.aws_region,
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            endpoint_url=settings.aws_endpoint_url,
        )


def get_client() -> DynamoDBClient:
    return session.create_client("dynamodb", **AWSClientConfig.from_settings().model_dump())


def get_table_name() -> str:
    return get_tomodachi_app_settings().DYNAMODB_TABLE_NAME


async def create_table() -> None:
    table_name = get_table_name()
    async with get_client() as client:
        try:
            await client.create_table(
                TableName=table_name,
                AttributeDefinitions=[
                    {
                        "AttributeName": "PK",
                        "AttributeType": "S",
                    },
                ],
                KeySchema=[
                    {
                        "AttributeName": "PK",
                        "KeyType": "HASH",
                    },
                ],
                BillingMode="PAY_PER_REQUEST",
            )
        except client.exceptions.ResourceInUseException:
            logger.info("dynamodb_table_already_exists", table_name=table_name)
        else:
            logger.info("dynamodb_table_created", table_name=table_name)

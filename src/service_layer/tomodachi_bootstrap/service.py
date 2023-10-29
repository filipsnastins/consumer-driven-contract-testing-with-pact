import uuid

import tomodachi
from aiohttp import web
from pydantic_settings import BaseSettings

from service_layer.tomodachi_bootstrap.logger import configure_structlog
from service_layer.tomodachi_bootstrap.middleware import (
    http_correlation_id_middleware,
    message_correlation_id_middleware,
    sns_sqs_message_retry_middleware,
    structlog_middleware,
)


class TomodachiBaseSettings(BaseSettings):
    environment: str
    aws_region: str
    aws_access_key_id: str | None = None
    aws_secret_access_key: str | None = None
    aws_endpoint_url: str | None = None
    aws_sns_topic_prefix: str = ""
    aws_sqs_queue_name_prefix: str = ""

    @property
    def is_dev_env(self) -> bool:
        return self.environment in ["development", "autotest"]


class TomodachiServiceBase(tomodachi.Service):
    http_middleware: list = [
        http_correlation_id_middleware,
        structlog_middleware,
    ]
    message_middleware: list = [
        sns_sqs_message_retry_middleware,
        message_correlation_id_middleware,
        structlog_middleware,
    ]

    def __init__(self) -> None:
        settings = TomodachiBaseSettings()  # type: ignore
        self.options = tomodachi.Options(
            aws_endpoint_urls=tomodachi.Options.AWSEndpointURLs(
                sns=settings.aws_endpoint_url,
                sqs=settings.aws_endpoint_url,
            ),
            aws_sns_sqs=tomodachi.Options.AWSSNSSQS(
                region_name=settings.aws_region,
                aws_access_key_id=settings.aws_access_key_id,
                aws_secret_access_key=settings.aws_secret_access_key,
                topic_prefix=settings.aws_sns_topic_prefix,
                queue_name_prefix=settings.aws_sqs_queue_name_prefix,
            ),
        )
        self.is_dev_env = settings.is_dev_env
        configure_structlog(renderer="dev" if self.is_dev_env else "json")

    @tomodachi.http("GET", r"/health/?", ignore_logging=[200])
    async def healthcheck(self, request: web.Request, correlation_id: uuid.UUID) -> web.Response:
        return web.json_response({"status": "ok"}, status=200)

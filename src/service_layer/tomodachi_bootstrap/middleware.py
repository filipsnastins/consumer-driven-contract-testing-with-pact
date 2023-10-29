import uuid
from typing import Any, Callable

import structlog
from aiohttp import web
from tomodachi.transport.aws_sns_sqs import AWSSNSSQSInternalServiceError

logger: structlog.stdlib.BoundLogger = structlog.get_logger()


async def sns_sqs_message_retry_middleware(func: Callable, *args: Any, **kwargs: Any) -> Any:
    try:
        return await func(*args, **kwargs)
    except Exception as exc:
        exception_name = exc.__class__.__name__
        logger.error("Retrying SNS SQS message due to unhandled exception", exception_name=exception_name)
        raise AWSSNSSQSInternalServiceError(exception_name) from exc


async def http_correlation_id_middleware(
    func: Callable, service: Any, request: web.Request, *args: Any, **kwargs: Any
) -> Any:
    correlation_id = request.headers.get("X-Correlation-Id", uuid.uuid4())
    if not isinstance(correlation_id, uuid.UUID):
        correlation_id = uuid.UUID(correlation_id)

    response = await func(*args, **kwargs, correlation_id=correlation_id)

    if isinstance(response, web.Response):
        response.headers["X-Correlation-Id"] = str(correlation_id)
    else:
        logger.warning(
            "HTTP correlation ID middleware did not receive a Response object;"
            " 'X-Correlation-Id' header will not be set",
            correlation_id=correlation_id,
        )

    return response


async def message_correlation_id_middleware(func: Callable, *args: Any, **kwargs: Any) -> Any:
    message = kwargs.get("message")

    if isinstance(message, dict):
        data = message.get("data")
        if isinstance(data, dict):
            correlation_id = data.get("correlation_id", uuid.uuid4())
        elif data and hasattr(data, "correlation_id"):
            correlation_id = data.correlation_id
        else:
            correlation_id = uuid.uuid4()
    elif hasattr(message, "correlation_id"):
        correlation_id = getattr(message, "correlation_id")  # noqa: B009
    else:
        correlation_id = uuid.uuid4()

    if not isinstance(correlation_id, uuid.UUID):
        correlation_id = uuid.UUID(correlation_id)

    return await func(*args, **kwargs, correlation_id=correlation_id)


async def structlog_middleware(func: Callable, *args: Any, **kwargs: Any) -> Any:
    correlation_id = str(kwargs.get("correlation_id", uuid.uuid4()))
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(correlation_id=correlation_id)

    return await func(*args, **kwargs)

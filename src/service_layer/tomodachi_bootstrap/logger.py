import logging
import sys
import uuid
from typing import Literal

import structlog
from structlog.types import EventDict


def cast_uuid_to_str_processor(logger: logging.Logger, method_name: str, event_dict: EventDict) -> EventDict:
    for key, value in event_dict.items():
        if isinstance(value, uuid.UUID):
            event_dict[key] = str(value)
    return event_dict


def configure_structlog(renderer: Literal["json", "dev", "key-value"] = "json", log_level: int = logging.INFO) -> None:
    processors = [
        structlog.contextvars.merge_contextvars,
        cast_uuid_to_str_processor,
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
    ]
    if renderer == "json":
        processors.extend(
            [
                structlog.processors.dict_tracebacks,
                structlog.processors.JSONRenderer(),
            ]
        )
    elif renderer == "dev":
        processors.extend(
            [
                structlog.processors.format_exc_info,
                structlog.processors.ExceptionPrettyPrinter(),
                structlog.dev.ConsoleRenderer(),
            ]
        )
    elif renderer == "key-value":
        processors.extend(
            [
                structlog.processors.format_exc_info,
                structlog.processors.KeyValueRenderer(),
            ]
        )
    logging.basicConfig(format="%(message)s", stream=sys.stdout, level=log_level)
    structlog.configure(
        processors=processors,  # type: ignore
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

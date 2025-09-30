"""Logging helpers for the FastAPI Template application."""

import logging
import logging.config
import sys
import traceback as _tb
import os
from loguru import logger


class UvicornHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:  # pragma: no cover - thin wrapper
        logger.log(
            record.levelname,
            record.getMessage(),
            extra={"location": "Uvicorn"},
        )


def setup_loguru(log_level: str = "INFO") -> None:
    logger.remove()
    logger.add(
        sys.stdout,
        level=log_level,
        format=base_formatter,
        backtrace=False,
        diagnose=False,
    )


def base_formatter(record: dict) -> str:
    if record["exception"]:
        tb = record["exception"].traceback
        frames = _tb.extract_tb(tb)

        user_frame = None
        for frame in reversed(frames):
            path = os.path.abspath(frame.filename)
            if "site-packages" not in path and "lib/python" not in path:
                user_frame = frame
                break

        if user_frame:
            location = f"{user_frame.filename}:{user_frame.name}:{user_frame.lineno}"
        else:

            last = frames[-1]
            location = f"{last.filename}:{last.name}:{last.lineno}"
    else:
        # normal logs
        location = f"{record['file'].name}:{record['function']}:{record['line']}"

    return (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level:<8}</level> | "
        f"<cyan>{location}</cyan> : "
        "<level>{message}</level>\n"
    )


def get_logging_dict(log_level: str = "INFO") -> dict:
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "handlers": {
            "UvicornHandler": {
                "level": log_level.upper(),
                "()": UvicornHandler,
            }
        },
        "loggers": {
            "uvicorn": {
                "level": log_level.upper(),
                "handlers": ["UvicornHandler"],
                "propagate": False,
            },
            "uvicorn.access": {
                "level": log_level.upper(),
                "handlers": [],
                "propagate": False,
            },
        },
    }


class Logger:
    def __init__(self, log_level: str = "INFO") -> None:
        setup_loguru(log_level)
        self.dict_config = get_logging_dict(log_level)
        logging.config.dictConfig(self.dict_config)

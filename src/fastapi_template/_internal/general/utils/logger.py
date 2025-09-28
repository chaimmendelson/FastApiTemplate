"""Logging helpers for the FastAPI template."""

import logging
import logging.config
import sys

from loguru import logger


class UvicornHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:  # pragma: no cover - thin wrapper
        logger.log(
            record.levelname,
            record.getMessage(),
            extra={"location": "Uvicorn"},
        )


def base_formatter(record: dict) -> str:
    extra = record.get("extra", {}).get("extra", {})
    location = extra.get("location", "{name}:{function}:{line}")
    return (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level:<8}</level> | "
        f"<cyan>{location}</cyan> - "
        "<level>{message}</level>\n"
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

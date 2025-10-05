"""Logging helpers for the FastAPI Template application."""

import logging
import logging.config
import sys
import traceback as _tb
import os
from loguru import logger
from uvicorn.config import LOGGING_CONFIG as UVICORN_LOGGING_CONFIG

PROJECT_ROOT = os.path.abspath(os.getenv("PROJECT_ROOT", os.getcwd()))
PY_VER = f"python{sys.version_info.major}.{sys.version_info.minor}"

def _in_package(path: str) -> bool:
    ap = os.path.abspath(path)
    return ("site-packages" in ap) or (f"{os.sep}lib{os.sep}{PY_VER}{os.sep}" in ap)

def _to_module(path: str) -> str:
    ap = os.path.abspath(path)
    if ap.startswith(PROJECT_ROOT):
        rel = os.path.relpath(ap, PROJECT_ROOT)
        if rel.endswith(".py"):
            rel = rel[:-3]
        return rel.replace(os.sep, ".")
    return os.path.basename(ap).removesuffix(".py")

class UvicornHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:  # pragma: no cover - thin wrapper
        logger.log(
            record.levelname,
            record.getMessage(),
            extra={"location": "Uvicorn"},
        )


def setup_loguru(log_level: str = "INFO") -> None:
    logger.opt(depth=1)
    logger.remove()
    logger.add(
        sys.stdout,
        level=log_level,
        format=base_formatter,
        backtrace=False,
        diagnose=False,
    )


def base_formatter(record: dict) -> str:
    # allow explicit override if you set extra={"location": "..."}
    override = record.get("extra", {}).get("extra", {}).get("location")
    if override:
        location = override
    else:
        # defaults from the call site
        module = record["name"]          # dotted module
        func = record["function"]
        line = record["line"]

        if record["exception"]:
            tb = record["exception"].traceback
            frames = _tb.extract_tb(tb)  # oldest -> newest
            chosen = None

            # prefer first frame under your project root
            for fr in reversed(frames):
                ap = os.path.abspath(fr.filename)
                if ap.startswith(PROJECT_ROOT) and not _in_package(ap):
                    chosen = fr
                    break

            # fallback, first non package frame
            if chosen is None:
                for fr in reversed(frames):
                    if not _in_package(fr.filename):
                        chosen = fr
                        break

            # final fallback, raise site
            if chosen is None and frames:
                chosen = frames[-1]

            if chosen:
                module = _to_module(chosen.filename)
                func = chosen.name
                line = chosen.lineno
        else:
            # regular logs, prefer module from file path when it is in your project
            ap = record["file"].path
            if ap and ap.startswith(PROJECT_ROOT) and not _in_package(ap):
                module = _to_module(ap)

        location = f"{module}:{func}:{line}"

    return (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level:<8}</level> | "
        f"<cyan>{location}</cyan> - "
        "<level>{message}</level>\n"
    )



def configure_uvicorn(log_level: str = "INFO") -> None:
    UVICORN_LOGGING_CONFIG["handlers"] = {
            "UvicornHandler": {
                "level": log_level.upper(),
                "()": UvicornHandler,
            }
        }

    UVICORN_LOGGING_CONFIG["loggers"] = {
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
        }


class Logger:
    def __init__(self, log_level: str = "INFO") -> None:
        setup_loguru(log_level)
        configure_uvicorn(log_level)

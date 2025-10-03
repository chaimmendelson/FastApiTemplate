"""Logging helpers for the FastAPI Template application."""

import logging
import logging.config
import sys
import traceback as _tb
import os
from typing import Iterable, List
from loguru import logger

PROJECT_ROOT = os.path.abspath(os.getenv("PROJECT_ROOT", os.getcwd()))
PY_VER = f"python{sys.version_info.major}.{sys.version_info.minor}"

def _in_package(path: str) -> bool:
    ap = os.path.abspath(path)
    return ("site-packages" in ap) or (f"{os.sep}lib{os.sep}{PY_VER}{os.sep}" in ap)

def _to_module(path: str) -> str:
    ap = os.path.abspath(path)
    module: str
    if ap.startswith(PROJECT_ROOT):
        rel = os.path.relpath(ap, PROJECT_ROOT)
        if rel.endswith(".py"):
            rel = rel[:-3]
        module = rel.replace(os.sep, ".")
    else:
        module = ""
        best_depth = None

        for entry in filter(None, sys.path):
            try:
                root = os.path.abspath(entry)
            except (OSError, RuntimeError):
                continue

            try:
                common = os.path.commonpath([ap, root])
            except ValueError:
                continue

            if common != root:
                continue

            rel = os.path.relpath(ap, root)
            if rel.startswith(".."):
                continue

            depth = rel.count(os.sep)
            candidate = os.path.splitext(rel)[0].replace(os.sep, ".")

            if not candidate:
                continue

            if best_depth is None or depth < best_depth:
                best_depth = depth
                module = candidate

        if not module:
            module = os.path.splitext(os.path.basename(ap))[0]
            if module == "__init__":
                parent = os.path.basename(os.path.dirname(ap))
                module = parent or module

    for needle in (".site-packages.", ".dist-packages."):
        if needle in module:
            module = module.split(needle, 1)[1]
            break

    for prefix in ("site-packages.", "dist-packages."):
        if module.startswith(prefix):
            module = module[len(prefix):]
            break

    if module.endswith(".__init__"):
        module = module[: -len(".__init__")]

    return module


def _format_frame(frame: _tb.FrameSummary) -> str:
    module = _to_module(frame.filename)
    return f"{module}:{frame.name}:{frame.lineno}"


def _exception_path(frames: Iterable[_tb.FrameSummary]) -> List[str]:
    frames_list = list(frames)
    selected: List[_tb.FrameSummary] = []
    seen = set()

    for frame in frames_list:
        ap = os.path.abspath(frame.filename)
        key = (frame.filename, frame.lineno, frame.name)
        if ap.startswith(PROJECT_ROOT) and not _in_package(ap):
            if key not in seen:
                selected.append(frame)
                seen.add(key)
        elif not selected and not _in_package(frame.filename):
            if key not in seen:
                selected.append(frame)
                seen.add(key)

    if frames_list:
        final = frames_list[-1]
        key = (final.filename, final.lineno, final.name)
        if key not in seen:
            selected.append(final)

    return [_format_frame(frame) for frame in selected]

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
        location = None

        if record["exception"]:
            tb = record["exception"].traceback
            frames = _tb.extract_tb(tb)  # oldest -> newest
            path_segments = _exception_path(frames)

            if path_segments:
                location = " -> ".join(path_segments)
            else:
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
                location = f"{module}:{func}:{line}"
        else:
            # regular logs, prefer module from file path when it is in your project
            ap = record["file"].path
            if ap and ap.startswith(PROJECT_ROOT) and not _in_package(ap):
                module = _to_module(ap)

        if location is None:
            location = f"{module}:{func}:{line}"

    return (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level:<8}</level> | "
        f"<cyan>{location}</cyan> - "
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

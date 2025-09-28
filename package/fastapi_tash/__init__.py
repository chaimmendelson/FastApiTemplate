"""FastAPI Tash package exposing the public application factory."""

from importlib import metadata

from .application import create_app

try:  # pragma: no cover - executed only when package metadata is present
    __version__ = metadata.version("fastapi-tash")
except metadata.PackageNotFoundError:  # pragma: no cover - local editable installs
    __version__ = "0.0.0"

__all__ = ["create_app", "__version__"]

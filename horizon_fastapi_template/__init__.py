"""FastAPI application template package."""
from ._internal import general_create_app
from ._internal.database.basic_api import BaseAPI

__all__ = ["general_create_app", "BaseAPI"]


def __getattr__(name: str):
    if name == "general_create_app":
        return general_create_app
    elif name == "BaseAPI":
        return BaseAPI
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

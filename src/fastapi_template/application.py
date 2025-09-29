"""Public application factory for the FastAPI template."""

from fastapi import FastAPI

from ._internal import settings, general_create_app, logger_config

async_background_tasks: list = []

def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    The returned application has two helpful attributes on ``app.state``:

    * ``settings`` – the resolved configuration values.
    * ``logger_config`` – the preconfigured logging dictionary.
    """

    app = general_create_app(
        async_background_tasks=async_background_tasks,
    )

    app.state.settings = settings
    app.state.logger_config = logger_config
    return app

"""Optional extension points for the FastAPI Tash package."""

from fastapi import FastAPI

async_background_tasks: list = []


def update_app(app: FastAPI) -> FastAPI:
    """Hook for extending the application instance."""

    return app

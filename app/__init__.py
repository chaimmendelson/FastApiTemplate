from fastapi import FastAPI

from .general import general_create_app

def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    """

    app = general_create_app()

    return app
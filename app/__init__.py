import json
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html
)
from fastapi.staticfiles import StaticFiles

from app.general import logger

def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    """
    app = FastAPI(docs_url=None, redoc_url=None)
    static_path = Path(__file__).parent / "static"
    app.mount("/static", StaticFiles(directory=static_path), name="static")

    @app.get("/docs", include_in_schema=False)
    async def custom_swagger_ui_html():
        return get_swagger_ui_html(
            title="Swagger UI",
            swagger_js_url="/static/swagger-ui-bundle.js",
            swagger_css_url="/static/swagger-ui.css",
            swagger_favicon_url="/static/favicon.ico",
            openapi_url="/static/openapi.json",
        )

    @app.get("/redoc", include_in_schema=False)
    async def redoc_html():
        return get_redoc_html(
            title="ReDoc",
            redoc_js_url="/static/redoc.standalone.js",
            redoc_favicon_url="/static/favicon.ico",
            openapi_url="/static/openapi.json",
        )

    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        """
        Middleware to log incoming requests.
        """

        logger.info(f"[Request] {request.method} {request.url.path}")
        response = await call_next(request)
        logger.info(f"[Response] {request.method} {request.url.path} {response.status_code}")
        return response

    @app.get("/", response_model=dict, status_code=200)
    def read_root():
        """
        Root endpoint that returns a simple message.
        """
        return {"message": "Hello, World!"}

    app.openapi()

    with open(Path(__file__).parent / "static" / "openapi.json", "w") as f:
        f.write(json.dumps(app.openapi(), indent=2))
    return app
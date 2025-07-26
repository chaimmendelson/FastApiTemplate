import time

from .utils import logger_config, config
from .database import basic_api
from .routes import routers, handlers

from pathlib import Path

from fastapi import FastAPI, Request
from starlette.staticfiles import StaticFiles
from loguru import logger


def general_create_app(
    *,
    enable_logging_middleware: bool = True,
    enable_root_route: bool = True,
    enable_exception_handlers: bool = True,
    **fastapi_kwargs
) -> FastAPI:
    """
    Create and configure the FastAPI application.

    Args:
        enable_logging_middleware: If True, add basic logging middleware.
        enable_root_route: If True, add the root '/' route.
        enable_exception_handlers: If True, add exception handlers.
        **fastapi_kwargs: Additional keyword arguments for FastAPI().
    """
    app = FastAPI(
        **fastapi_kwargs,
        docs_url=None,
        redoc_url=None,
        openapi_url=config.SWAGGER_OPENAPI_JSON_URL
    )

    static_files_path = Path(__file__).parent.parent / "static"
    app.mount("/static", StaticFiles(directory=static_files_path), name="static")

    for router in routers:
        app.include_router(router)

    if enable_exception_handlers:
        for handler in handlers:
            app.add_exception_handler(handler.exception_class, handler.handler)

    @app.get(config.SWAGGER_OPENAPI_JSON_URL, include_in_schema=False)
    async def get_openapi():
        """
        Endpoint to serve the OpenAPI schema.
        """
        return app.openapi()

    if enable_logging_middleware:
        @app.middleware("http")
        async def log_requests(request: Request, call_next):
            """
            Middleware to log incoming requests.
            """
            logger.info(f"[Request] {request.method} {request.url.path}")

            start_time = time.perf_counter_ns()

            response = await call_next(request)

            process_time = time.perf_counter_ns() - start_time
            response.headers["X-Process-Time"] = str(process_time)

            logger.info(f"[Response] {request.method} {request.url.path} {response.status_code} {process_time}")

            return response

    if enable_root_route:
        @app.get("/", response_model=dict, status_code=200)
        def read_root():
            """
            Root endpoint that returns a simple message.
            """
            return {"message": f"Welcome to the {config.APP_NAME}!"}

    return app

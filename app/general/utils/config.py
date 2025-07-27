from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class BasicSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    PORT: int = Field(
        default=8000,
        description="The port the application will run on.",
        examples=[8000, 8080],
    )

    DEV_MODE: bool = Field(
        default=False,
        description="Enable development mode for the application.",
        examples=[True, False],
    )

    if DEV_MODE == True:

        LOG_LEVEL: str = Field(
            default="DEBUG",
            description="Logging level for the application.",
            examples=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        )

        RELOAD_INCLUDES: list[str] = Field(
            default=["*.py", ".env", "*.css", "*.js"],
            description="File patterns to watch for changes in development mode.",
            examples=[["*.py", "*.env"]],
        )

    else:

        RELOAD_INCLUDES: list[str] = Field(
            default=[],
            description="File patterns to watch for changes in production mode.",
            examples=[[]],
        )

        LOG_LEVEL: str = Field(
            default="INFO",
            description="Logging level for the application.",
            examples=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        )

    APP_NAME: str = Field(
        default="MyApp",
        description="The name of the application.",
        examples=["UserService", "PaymentAPI"],
    )

    PROCESS_TIME_HEADER: str = Field(
        default="X-Process-Time",
        description="Header name to include process time in responses.",
        examples=["X-Process-Time", "X-Response-Time"],
    )

    SWAGGER_STATIC_FILES: str = Field(
        default="/static/swagger",
        description="URL path to serve Swagger UI static files.",
        examples=["/static/swagger"],
    )

    SWAGGER_OPENAPI_JSON_URL: str = Field(
        default="/openapi.json",
        description="Endpoint URL for OpenAPI JSON schema.",
        examples=["/openapi.json"],
    )

    LOG_REQUEST_EXCLUDE_PATHS: list[str] = Field(
        default=["/health", "/metrics", "/static", "/docs", "/redoc", "/openapi.json", "/.well-known"],
        description="List of paths to ignore for logging.",
        examples=[["/health", "/metrics"]],
    )
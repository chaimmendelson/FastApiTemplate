from pydantic import ValidationError

from app.general.utils.logger import Logger
from app.general.utils.config import BasicSettings


def update_basic_settings(settings: BasicSettings):
    if settings.PROXIED and not settings.PROXY_LISTEN_PATH == "/":
        settings.PROXY_LISTEN_PATH = settings.PROXY_LISTEN_PATH.rstrip("/") + "/"
        settings.SWAGGER_STATIC_FILES = (
                settings.PROXY_LISTEN_PATH +
                settings.SWAGGER_STATIC_FILES.lstrip("/")
        )
        settings.SWAGGER_OPENAPI_JSON_URL = (
                settings.PROXY_LISTEN_PATH +
                settings.OPENAPI_JSON_URL.lstrip("/")
        )
    else:
        settings.PROXY_LISTEN_PATH = ""


try:
    basicSettings = BasicSettings()
    update_basic_settings(basicSettings)
except ValidationError as e:
    print(
        f"Configuration error: {e}\n"
        "Please ensure that all required environment variables are set correctly."
    )
    exit(1)

logger_config = Logger(basicSettings.LOG_LEVEL)
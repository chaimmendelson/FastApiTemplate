from pydantic import ValidationError

from .logger import get_logger, Logger
from .config import Settings

try:
    config = Settings()
except ValidationError as e:
    print(
        f"Configuration error: {e}\n"
        "Please ensure that all required environment variables are set correctly."
    )
    exit(1)

logger_config = Logger(config.LOG_LEVEL)
logger = get_logger()
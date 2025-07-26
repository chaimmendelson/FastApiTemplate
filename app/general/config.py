from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")
    PORT: int
    LOG_LEVEL: str = "INFO"
    APP_NAME: str = "MyApp"

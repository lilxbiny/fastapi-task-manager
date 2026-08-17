"""
Application configuration.

All settings are read from environment variables (see .env.example).
We use pydantic-settings so values are validated at startup instead of
failing later with a cryptic error.
"""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = (
        "postgresql+psycopg2://taskuser:taskpassword@db:5432/taskdb"
    )

    # Security
    SECRET_KEY: str = "change_this_to_a_long_random_secret_key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Misc
    PROJECT_NAME: str = "Task Management API"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance so we don't re-parse env vars every call."""
    return Settings()


settings = get_settings()

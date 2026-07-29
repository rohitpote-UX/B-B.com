"""
Brand Battle - Application Configuration
Loads settings from environment variables with sensible defaults.
Supports PostgreSQL, Redis, Celery, and Security parameters.
"""

from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Brand Battle"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENV: str = "development"

    # Database (PostgreSQL / SQLite)
    DATABASE_URL: str = "sqlite:///./brandbattle.db"
    POSTGRES_USER: str = "brandbattle"
    POSTGRES_PASSWORD: str = "brandbattle_secret_2026"
    POSTGRES_DB: str = "brandbattle_db"
    POSTGRES_HOST: str = ""
    POSTGRES_PORT: str = "5432"

    @property
    def effective_database_url(self) -> str:
        """Returns PostgreSQL URL if POSTGRES_HOST is provided, otherwise defaults to DATABASE_URL."""
        if self.POSTGRES_HOST:
            return (
                f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
                f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
            )
        return self.DATABASE_URL

    # JWT Auth & Security
    SECRET_KEY: str = "brand-battle-dev-secret-key-2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    ALLOWED_HOSTS: str = "*"

    # Redis Caching & Celery Broker
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_CACHE_TTL: int = 3600  # Default 1 hour
    REDIS_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 120

    # OpenAI
    OPENAI_API_KEY: str = ""

    # External APIs
    DUMMYJSON_BASE_URL: str = "https://dummyjson.com"

    # CORS
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    @property
    def allowed_hosts_list(self) -> List[str]:
        return [host.strip() for host in self.ALLOWED_HOSTS.split(",")]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()

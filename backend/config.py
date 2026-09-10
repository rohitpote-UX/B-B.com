"""
Brand Battle - Application Configuration
Loads settings from environment variables with sensible defaults.
Supports PostgreSQL, Redis, Celery, and Security parameters.
"""

try:
    from pydantic_settings import BaseSettings  # type: ignore
except ImportError:
    try:
        from pydantic import BaseSettings  # type: ignore
    except ImportError:
        class BaseSettings:  # type: ignore
            pass
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
        """Returns PostgreSQL URL if POSTGRES_HOST is provided, otherwise defaults to DATABASE_URL.
        Normalizes postgres:// to postgresql:// for SQLAlchemy 2.0+ and Render compatibility."""
        if self.POSTGRES_HOST:
            url = (
                f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
                f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
            )
        else:
            url = self.DATABASE_URL
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        return url

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

    # Data Trust Hardening — Freshness TTL Tiers (seconds)
    PRICE_TTL_HOT: int = 1800           # 30 minutes
    PRICE_TTL_STANDARD: int = 21600     # 6 hours
    PRICE_TTL_LOW_PRIORITY: int = 86400  # 24 hours
    IMAGE_TTL: int = 86400              # 24 hours
    ANOMALY_THRESHOLD_PCT: float = 40.0  # 40% price change anomaly flag

    # OpenAI
    OPENAI_API_KEY: str = ""

    # External APIs
    DUMMYJSON_BASE_URL: str = "https://dummyjson.com"

    # CORS
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000,https://brandbattle.in,https://www.brandbattle.in"

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

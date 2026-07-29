"""
Brand Battle - Structured Logging Setup
Provides environment-aware logging formatters for API requests, database queries, and system events.
"""

import logging
import sys
from config import settings


def setup_logging():
    """Configures structured application logging."""
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO
    
    log_format = (
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        if settings.ENV == "development"
        else '{"time": "%(asctime)s", "level": "%(levelname)s", "module": "%(name)s", "message": "%(message)s"}'
    )

    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

    # Silence verbose third-party loggers
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)


logger = logging.getLogger("brandbattle")

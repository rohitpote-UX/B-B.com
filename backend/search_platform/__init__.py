"""
Brand Battle — Enterprise AI Commerce Search Platform Package
Main entry point for the Search Service, Orchestrator, and REST Router.
"""

from search_platform.search_service import search_service
from search_platform.search_orchestrator import search_orchestrator
from search_platform.config import search_config
from search_platform.api import router as search_router
from search_platform.metrics import search_metrics
from search_platform.analytics import search_analytics
from search_platform.feedback import search_feedback
from search_platform.history import search_history_logger
from search_platform.search_cache import search_cache

__all__ = [
    "search_service",
    "search_orchestrator",
    "search_config",
    "search_router",
    "search_metrics",
    "search_analytics",
    "search_feedback",
    "search_history_logger",
    "search_cache",
]

"""
Brand Battle — Enterprise AI Recommendation Engine Package
Main entry point for Recommendation Service Orchestrator, REST Router, and Engine sub-modules.
"""

from recommendation_engine.recommendation_service import recommendation_orchestrator, RecommendationService
from recommendation_engine.recommendation_config import recommendation_settings
from recommendation_engine.api import router as recommendation_router
from recommendation_engine.recommendation_metrics import recommendation_metrics_collector
from recommendation_engine.recommendation_history import recommendation_history_logger
from recommendation_engine.feedback_collector import feedback_collector_service
from recommendation_engine.ab_testing import ab_testing_allocator

__all__ = [
    "recommendation_orchestrator",
    "RecommendationService",
    "recommendation_settings",
    "recommendation_router",
    "recommendation_metrics_collector",
    "recommendation_history_logger",
    "feedback_collector_service",
    "ab_testing_allocator"
]

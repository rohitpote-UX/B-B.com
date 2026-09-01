"""
Brand Battle — Enterprise Decision Intelligence & Analytics Platform Package
Exports router, service, collector, scheduler, and observability metrics.
"""

from analytics_platform.routers import router as analytics_router
from analytics_platform.services import analytics_platform_service
from analytics_platform.config import analytics_config
from analytics_platform.metrics import analytics_metrics
from analytics_platform.cache import analytics_cache
from analytics_platform.event_collector import universal_event_collector
from analytics_platform.scheduler import analytics_scheduler

__all__ = [
    "analytics_router",
    "analytics_platform_service",
    "analytics_config",
    "analytics_metrics",
    "analytics_cache",
    "universal_event_collector",
    "analytics_scheduler",
]

"""
Brand Battle — Enterprise Affiliate Commerce Platform Package
Exports router, service, provider registry, and metrics singletons.
"""

from affiliate_platform.routers import router as affiliate_router
from affiliate_platform.services import affiliate_platform_service
from affiliate_platform.config import affiliate_config
from affiliate_platform.provider_registry import provider_registry
from affiliate_platform.deeplink_generator import deeplink_generator
from affiliate_platform.metrics import affiliate_metrics
from affiliate_platform.scheduler import affiliate_scheduler

__all__ = [
    "affiliate_router",
    "affiliate_platform_service",
    "affiliate_config",
    "provider_registry",
    "deeplink_generator",
    "affiliate_metrics",
    "affiliate_scheduler",
]

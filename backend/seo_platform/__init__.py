"""
Brand Battle — Enterprise SEO Comparison Publishing Platform Package
Exports router, service, metadata engine, and validator singletons.
"""

from seo_platform.routers import router as seo_router
from seo_platform.services import seo_platform_service
from seo_platform.config import seo_config
from seo_platform.slug_generator import slug_generator_engine
from seo_platform.metadata_engine import dynamic_metadata_engine
from seo_platform.schema_validator import automated_seo_quality_validator

__all__ = [
    "seo_router",
    "seo_platform_service",
    "seo_config",
    "slug_generator_engine",
    "dynamic_metadata_engine",
    "automated_seo_quality_validator",
]

"""
Brand Battle — Enterprise Catalog Ingestion Engine
"""

from catalog_engine.base_adapter import BaseCatalogAdapter
from catalog_engine.schemas import NormalizedProductCandidate, JobProgressResponse, CatalogSourceSchema, CatalogMetricsResponse
from catalog_engine.normalizer import CatalogNormalizer
from catalog_engine.gtin_validator import GtinValidator
from catalog_engine.deduplicator import CatalogDeduplicator
from catalog_engine.quality_scorer import ProductQualityScorer
from catalog_engine.resolver import ProductIdentityResolver
from catalog_engine.security import is_ssrf_safe_url, AdaptiveRateLimiter
from catalog_engine.job_runner import CatalogJobRunner

__all__ = [
    "BaseCatalogAdapter",
    "NormalizedProductCandidate",
    "JobProgressResponse",
    "CatalogSourceSchema",
    "CatalogMetricsResponse",
    "CatalogNormalizer",
    "GtinValidator",
    "CatalogDeduplicator",
    "ProductQualityScorer",
    "ProductIdentityResolver",
    "is_ssrf_safe_url",
    "AdaptiveRateLimiter",
    "CatalogJobRunner",
]

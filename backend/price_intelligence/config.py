"""
Brand Battle — Enterprise AI Price Intelligence Configuration
Centralized settings, scoring weights, threshold limits, cache TTLs, and performance targets.
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, List


class ScoringWeights(BaseModel):
    """Configurable signal weights for Buy Confidence and Opportunity Score."""
    price_quality: float = 0.25
    historical_discount: float = 0.20
    seller_trust: float = 0.15
    price_forecast: float = 0.15
    volatility: float = 0.10
    user_affinity: float = 0.10
    warranty_value: float = 0.05


class PerformanceTargets(BaseModel):
    """Latency SLO targets (milliseconds)."""
    cached_lookup_ms: int = 50
    forecast_generation_ms: int = 500
    recommendation_ms: int = 200
    p95_latency_ms: int = 150


class CacheTTLConfig(BaseModel):
    """Redis cache TTLs (seconds)."""
    price_report_ttl: int = 300       # 5 minutes
    forecast_ttl: int = 1800          # 30 minutes
    marketplace_trust_ttl: int = 3600  # 1 hour
    fair_value_ttl: int = 1800        # 30 minutes
    opportunity_score_ttl: int = 600  # 10 minutes


class PriceIntelligenceConfig(BaseModel):
    """Master configuration for the Enterprise Price Intelligence Platform."""
    enabled: bool = True
    algorithm_version: str = "v5.0.0-enterprise-price-intelligence"
    weights: ScoringWeights = ScoringWeights()
    performance: PerformanceTargets = PerformanceTargets()
    cache_ttl: CacheTTLConfig = CacheTTLConfig()

    # Thresholds
    fake_discount_threshold_pct: float = 15.0  # >15% difference from 90-day avg MRP
    high_volatility_threshold: float = 0.25    # stddev / mean > 0.25
    excellent_deal_threshold: float = 85.0
    good_deal_threshold: float = 65.0
    overpriced_threshold: float = 40.0

    # Feature flags
    enable_redis_cache: bool = True
    enable_forecasting: bool = True
    enable_fake_discount_detection: bool = True
    enable_bundle_recommendations: bool = True
    enable_tco_calculation: bool = True
    enable_explainability: bool = True


price_intel_config = PriceIntelligenceConfig()

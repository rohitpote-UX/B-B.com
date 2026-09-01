"""
Brand Battle — Recommendation Engine Configuration
Centralized settings, scoring weights, threshold limits, cache TTLs, and strategy defaults.
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, List


class ScoringWeights(BaseModel):
    relationship_weight: float = 0.25
    similarity_weight: float = 0.20
    value_weight: float = 0.15
    popularity_weight: float = 0.15
    price_alignment_weight: float = 0.15
    trending_weight: float = 0.10


class RecommendationThresholds(BaseModel):
    min_confidence: float = 0.40
    min_similarity_score: float = 0.35
    budget_max_ratio: float = 0.85  # Product <= 85% of baseline price
    upgrade_min_ratio: float = 1.15  # Product >= 115% of baseline price
    upgrade_max_ratio: float = 2.50  # Up to 250% of baseline price
    max_recommendation_results: int = 20
    default_page_size: int = 10


class CacheTTLConfig(BaseModel):
    product_recommendation_ttl: int = 3600  # 1 hour
    trending_ttl: int = 900  # 15 mins
    popular_ttl: int = 1800  # 30 mins
    personal_ttl: int = 600  # 10 mins
    anonymous_ttl: int = 300  # 5 mins


class RecommendationConfig(BaseModel):
    enabled: bool = True
    algorithm_version: str = "v3.0.0-enterprise"
    weights: ScoringWeights = ScoringWeights()
    thresholds: RecommendationThresholds = RecommendationThresholds()
    cache_ttl: CacheTTLConfig = CacheTTLConfig()
    enable_redis_cache: bool = True
    enable_ab_testing: bool = True
    ab_test_active_variant: str = "variant_a_hybrid"  # variant_a_hybrid, variant_b_value, variant_c_behavioral


recommendation_settings = RecommendationConfig()

"""
Brand Battle — Enterprise AI Commerce Search Platform
Centralized configuration for scoring weights, performance targets, cache TTLs,
candidate pool limits, and all configurable search parameters.
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, List


class QueryParserConfig(BaseModel):
    """Configuration for query parsing behavior."""
    price_pattern_keywords: List[str] = [
        "under", "below", "less than", "max", "upto", "up to",
        "above", "over", "more than", "min", "minimum", "starting",
        "between", "from", "to", "range"
    ]
    currency_symbols: List[str] = ["$", "₹", "€", "£", "¥"]
    superlative_keywords: List[str] = [
        "best", "top", "premium", "cheapest", "budget", "affordable",
        "luxury", "flagship", "popular", "trending", "latest", "newest"
    ]
    comparison_keywords: List[str] = ["vs", "versus", "compared", "or", "better", "compare"]
    question_keywords: List[str] = ["best", "which", "what", "recommend", "suggest", "good", "review", "reviews"]
    deal_keywords: List[str] = ["deal", "deals", "offer", "offers", "discount", "sale", "coupon", "cashback"]


class ScoringWeights(BaseModel):
    """Configurable signal weights for composite ranking (must sum to ~1.0)."""
    keyword_relevance: float = 0.15
    semantic_similarity: float = 0.12
    kg_confidence: float = 0.10
    brand_reliability: float = 0.08
    marketplace_reliability: float = 0.05
    offer_freshness: float = 0.05
    price_competitiveness: float = 0.08
    product_completeness: float = 0.04
    popularity: float = 0.08
    trending: float = 0.06
    availability: float = 0.04
    review_quality: float = 0.05
    recommendation_affinity: float = 0.04
    user_preference: float = 0.03
    historical_ctr: float = 0.02
    attribute_match: float = 0.01


class RerankingConfig(BaseModel):
    """AI re-ranking configuration."""
    intent_boost_factor: float = 1.15
    diversity_penalty: float = 0.92  # Penalize same-brand clusters
    price_value_boost: float = 1.10
    freshness_recency_boost: float = 1.05
    quality_completeness_boost: float = 1.08
    max_same_brand_top5: int = 2  # Max same-brand products in top-5


class PerformanceTargets(BaseModel):
    """Latency SLO targets (milliseconds)."""
    autocomplete_ms: int = 20
    cached_search_ms: int = 30
    fresh_search_ms: int = 120
    semantic_search_ms: int = 150
    p95_latency_ms: int = 250


class CacheTTLConfig(BaseModel):
    """Redis cache TTLs (seconds)."""
    query_result_ttl: int = 60
    autocomplete_ttl: int = 30
    popular_query_ttl: int = 300
    facet_ttl: int = 120
    trending_ttl: int = 180
    suggestion_ttl: int = 60
    search_history_ttl: int = 3600


class CandidatePoolConfig(BaseModel):
    """Candidate generation limits."""
    max_candidates: int = 800
    min_candidates: int = 20
    kg_expansion_limit: int = 100
    trending_expansion_limit: int = 50
    keyword_retrieval_limit: int = 300
    semantic_retrieval_limit: int = 200
    attribute_retrieval_limit: int = 200
    marketplace_retrieval_limit: int = 200


class SpellCorrectionConfig(BaseModel):
    """Spell correction thresholds."""
    max_edit_distance: int = 2
    min_confidence: float = 0.65
    min_word_length: int = 3
    protected_terms: List[str] = [
        "iphone", "macbook", "oneplus", "samsung", "airpods", "playstation",
        "xbox", "nintendo", "razer", "asus", "lenovo", "dell", "acer"
    ]


class SearchPlatformConfig(BaseModel):
    """Master configuration for the Enterprise Search Platform."""
    enabled: bool = True
    algorithm_version: str = "v4.0.0-enterprise-search"
    parser: QueryParserConfig = QueryParserConfig()
    weights: ScoringWeights = ScoringWeights()
    reranking: RerankingConfig = RerankingConfig()
    performance: PerformanceTargets = PerformanceTargets()
    cache_ttl: CacheTTLConfig = CacheTTLConfig()
    candidates: CandidatePoolConfig = CandidatePoolConfig()
    spell_correction: SpellCorrectionConfig = SpellCorrectionConfig()

    # Feature flags
    enable_semantic_search: bool = True
    enable_kg_search: bool = True
    enable_spell_correction: bool = True
    enable_synonyms: bool = True
    enable_personalization: bool = True
    enable_reranking: bool = True
    enable_redis_cache: bool = True
    enable_analytics: bool = True

    # Pagination
    default_page_size: int = 20
    max_page_size: int = 100
    max_autocomplete_results: int = 10


search_config = SearchPlatformConfig()

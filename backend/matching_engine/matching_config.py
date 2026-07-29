"""
Brand Battle - Hybrid AI Matching Engine Configuration
Central configuration for signal weights, category-specific thresholds,
price tolerances, and embedding provider settings.
"""

from typing import Dict, Any

# Decision Thresholds
THRESHOLD_AUTO_MATCH = 0.72
THRESHOLD_REVIEW_QUEUE = 0.50

# Category-Specific Auto-Match Thresholds
CATEGORY_THRESHOLDS: Dict[str, float] = {
    "Smartphones": 0.75,
    "Laptops": 0.72,
    "Headphones": 0.70,
    "Watches": 0.70,
    "Shoes": 0.65,
    "Clothing": 0.60,
    "default": 0.68,
}

# Signal Weights for Ensemble Scoring (must sum to 1.0)
SIGNAL_WEIGHTS: Dict[str, float] = {
    "title_similarity": 0.25,
    "brand_match": 0.20,
    "model_token_overlap": 0.15,
    "semantic_embedding": 0.15,
    "attribute_match": 0.10,
    "spec_similarity": 0.08,
    "category_match": 0.04,
    "price_similarity": 0.03,
}

# Price Tolerance Configuration (% price variance window)
PRICE_TOLERANCE_PCT = 0.40  # 40% variance window

# Embedding Configuration
EMBEDDING_MODEL_VERSION = "tf_idf_v1_ngram"
EMBEDDING_CACHE_TTL = 86400  # 24 hours

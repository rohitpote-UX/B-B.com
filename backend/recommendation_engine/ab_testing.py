"""
Brand Battle — A/B Testing & Strategy Allocation Engine
Allocates users/sessions to active recommendation experiment variants and tracks conversion performance.
"""

from typing import Dict, Any, Optional
import hashlib
from recommendation_engine.recommendation_config import recommendation_settings
from logging_config import logger


class ABTestingEngine:
    """Assigns experiment variants (Variant A: Hybrid Graph, Variant B: Value-First, Variant C: Behavioral) consistently."""

    VARIANTS = ["variant_a_hybrid", "variant_b_value", "variant_c_behavioral"]

    def assign_variant(self, user_id_or_session: str) -> str:
        """Deterministically map user/session to an experiment variant using hash bucket."""
        if not recommendation_settings.enable_ab_testing:
            return recommendation_settings.ab_test_active_variant

        if not user_id_or_session:
            return "variant_a_hybrid"

        hash_digest = hashlib.md5(user_id_or_session.encode('utf-8')).hexdigest()
        hash_num = int(hash_digest, 16)
        index = hash_num % len(self.VARIANTS)
        return self.VARIANTS[index]

    def get_variant_config(self, variant: str) -> Dict[str, Any]:
        """Return algorithm scoring weights for assigned variant."""
        if variant == "variant_b_value":
            return {
                "variant": "variant_b_value",
                "value_weight": 0.45,
                "relationship_weight": 0.15,
                "similarity_weight": 0.15,
                "popularity_weight": 0.15,
                "trending_weight": 0.10
            }
        elif variant == "variant_c_behavioral":
            return {
                "variant": "variant_c_behavioral",
                "popularity_weight": 0.35,
                "trending_weight": 0.35,
                "relationship_weight": 0.10,
                "similarity_weight": 0.10,
                "value_weight": 0.10
            }
        else:
            return {
                "variant": "variant_a_hybrid",
                "relationship_weight": 0.25,
                "similarity_weight": 0.20,
                "value_weight": 0.15,
                "popularity_weight": 0.15,
                "trending_weight": 0.15
            }


ab_testing_allocator = ABTestingEngine()

"""
Brand Battle — Recommendation Validator
AI validation layer ensuring zero cross-category recommendation leaks.
"""

from typing import List, Dict, Any, Tuple
from recommendation_engine.category_resolver import category_resolver


class RecommendationValidator:
    """Validates candidate recommendations against source product taxonomy."""

    def validate_recommendation(self, target_product: Any, candidate_product: Any) -> Tuple[bool, str]:
        """
        Validates that candidate_product belongs to the same category & subcategory as target_product.
        Returns (is_valid, reason).
        """
        target_cat, target_sub, _ = category_resolver.resolve_product_taxonomy(target_product)
        cand_cat, cand_sub, _ = category_resolver.resolve_product_taxonomy(candidate_product)

        if target_cat != cand_cat:
            return (False, f"Category mismatch: {target_cat} vs {cand_cat}")

        if target_sub != cand_sub:
            return (False, f"Subcategory mismatch: {target_sub} vs {cand_sub}")

        return (True, "Category & Subcategory validated")

    def validate_and_purge_list(self, target_product: Any, recommendation_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Purges any non-matching candidates from final output list."""
        validated = []
        for item in recommendation_list:
            cand = item.get("product") or item
            is_valid, _ = self.validate_recommendation(target_product, cand)
            if is_valid:
                validated.append(item)
        return validated


recommendation_validator = RecommendationValidator()

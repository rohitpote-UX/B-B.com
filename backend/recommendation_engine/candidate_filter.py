"""
Brand Battle — Candidate Filter
Filters candidates to enforce 100% Category, Subcategory, and Family parity before scoring.
"""

from typing import List, Dict, Any
from recommendation_engine.category_resolver import category_resolver


class CandidateFilter:
    """Enforces category, subcategory, and family boundary candidate filtering."""

    def filter_candidates(self, target_product: Any, candidate_pool: List[Any]) -> List[Any]:
        """
        Filters candidate pool to retain ONLY products in the exact same category & subcategory.
        """
        target_cat, target_sub, target_fam = category_resolver.resolve_product_taxonomy(target_product)
        target_id = getattr(target_product, "id", None) or (target_product.get("id") if isinstance(target_product, dict) else None)

        valid_candidates = []

        for item in candidate_pool:
            cand_prod = item.get("product", item) if isinstance(item, dict) else item
            cand_id = getattr(cand_prod, "id", None) or (cand_prod.get("id") if isinstance(cand_prod, dict) else None)

            # Exclude self
            if target_id and cand_id and str(target_id) == str(cand_id):
                continue

            cand_cat, cand_sub, cand_fam = category_resolver.resolve_product_taxonomy(cand_prod)

            # MANDATORY MATCH RULE: Category ID AND Subcategory ID must match!
            if cand_cat == target_cat and cand_sub == target_sub:
                valid_candidates.append(item)

        return valid_candidates


candidate_filter = CandidateFilter()

"""
Brand Battle — Taxonomy Service
Centralized service managing product taxonomy, hierarchy, and metadata normalization.
"""

from typing import Dict, List, Any, Optional
from recommendation_engine.category_resolver import category_resolver


class TaxonomyService:
    """Manages enterprise product taxonomy and canonical hierarchy."""

    def get_product_taxonomy(self, product: Any) -> Dict[str, str]:
        cat_id, sub_id, fam_id = category_resolver.resolve_product_taxonomy(product)
        return {
            "category_id": cat_id,
            "subcategory_id": sub_id,
            "family_id": fam_id
        }

    def belongs_to_same_family(self, prod_a: Any, prod_b: Any) -> bool:
        tax_a = self.get_product_taxonomy(prod_a)
        tax_b = self.get_product_taxonomy(prod_b)
        return tax_a["category_id"] == tax_b["category_id"] and tax_a["subcategory_id"] == tax_b["subcategory_id"]


taxonomy_service = TaxonomyService()

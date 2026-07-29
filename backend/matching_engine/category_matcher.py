"""
Brand Battle - Category Matcher Module
Taxonomy tree distance & subcategory equivalence evaluator.
"""

from typing import Dict, Any, Optional


class CategoryMatcher:
    """Evaluates taxonomy similarity between listing and master candidate."""

    def evaluate(
        self,
        cat1: Optional[str],
        cat2: Optional[str],
        subcat1: Optional[str] = None,
        subcat2: Optional[str] = None
    ) -> Dict[str, Any]:
        """Calculates category taxonomy similarity score (0.0 to 1.0)."""
        if not cat1 or not cat2:
            return {"score": 0.5, "explanation": "Category unknown"}

        c1 = cat1.strip().lower()
        c2 = cat2.strip().lower()

        if c1 == c2:
            if subcat1 and subcat2 and subcat1.strip().lower() == subcat2.strip().lower():
                return {"score": 1.0, "explanation": f"Exact category & subcategory match: '{cat1}' > '{subcat1}'"}
            return {"score": 0.9, "explanation": f"Exact main category match: '{cat1}'"}

        # Partial/Related categories
        related_groups = [
            {"smartphones", "tablets", "electronics"},
            {"shoes", "footwear", "sneakers"},
            {"clothing", "apparel", "shirts"},
            {"headphones", "audio", "speakers"},
            {"watches", "smartwatches", "accessories"},
        ]

        for group in related_groups:
            if c1 in group and c2 in group:
                return {"score": 0.7, "explanation": f"Related taxonomy group match: '{cat1}' & '{cat2}'"}

        return {"score": 0.2, "explanation": f"Category mismatch: '{cat1}' != '{cat2}'"}


category_matcher = CategoryMatcher()

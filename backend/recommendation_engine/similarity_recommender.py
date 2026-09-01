"""
Brand Battle — Specification & Attribute Similarity Recommender
Calculates technical specification similarity, numeric feature overlap, and category attribute distance.
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from models import Product
from logging_config import logger


class SimilarityRecommender:
    """Computes technical spec and attribute similarity between products."""

    def compute_spec_similarity(self, specs_a: Optional[Dict[str, Any]], specs_b: Optional[Dict[str, Any]]) -> float:
        """Compute Jaccard & Key-Value overlap score for specifications."""
        if not specs_a or not specs_b:
            return 0.0

        keys_a = set(specs_a.keys())
        keys_b = set(specs_b.keys())
        
        if not keys_a or not keys_b:
            return 0.0

        common_keys = keys_a.intersection(keys_b)
        union_keys = keys_a.union(keys_b)

        if not union_keys:
            return 0.0

        key_jaccard = len(common_keys) / len(union_keys)
        
        matching_values = 0
        for k in common_keys:
            val_a = str(specs_a[k]).lower().strip()
            val_b = str(specs_b[k]).lower().strip()
            if val_a == val_b or val_a in val_b or val_b in val_a:
                matching_values += 1

        val_match_score = matching_values / len(common_keys) if common_keys else 0.0
        
        return round(0.4 * key_jaccard + 0.6 * val_match_score, 4)

    def get_similar_spec_products(
        self, 
        db: Session, 
        product: Product, 
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Find category-matched products with high technical specification similarity."""
        try:
            candidates = db.query(Product).filter(
                Product.category_id == product.category_id,
                Product.id != product.id,
                Product.is_active == True
            ).limit(50).all()

            results = []
            for candidate in candidates:
                sim_score = self.compute_spec_similarity(product.specifications, candidate.specifications)
                if sim_score >= 0.25:
                    results.append({
                        "product": candidate,
                        "similarity_score": sim_score,
                        "reason": f"{int(sim_score * 100)}% Specification & Hardware Similarity"
                    })

            results.sort(key=lambda x: x["similarity_score"], reverse=True)
            return results[:limit]
        except Exception as e:
            logger.error(f"Error computing spec similarity for product {product.id}: {e}")
            return []

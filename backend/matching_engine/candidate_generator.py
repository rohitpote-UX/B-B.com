"""
Brand Battle - Candidate Generator
Fast candidate retrieval layer that pre-filters candidate MasterProducts by brand,
category, price window, and model series to eliminate unnecessary comparisons.
"""

from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import or_
import logging

import models
from matching_engine.matching_config import PRICE_TOLERANCE_PCT

logger = logging.getLogger("brandbattle.matching.candidate")


class CandidateGenerator:
    """Pre-filters and ranks candidate MasterProducts before evaluation."""

    def retrieve_candidates(
        self,
        features: Dict[str, Any],
        db: Session,
        max_candidates: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Retrieves a ranked subset of candidate MasterProducts matching brand/category/price constraints.
        """
        brand_name = features.get("brand", "")
        cat_name = features.get("category", "")
        price = features.get("price", 0.0)

        q = db.query(models.MasterProduct).filter(models.MasterProduct.is_active == True)

        # 1. Pre-filter by Brand if known
        if brand_name:
            brand_obj = db.query(models.Brand).filter(models.Brand.name.ilike(brand_name)).first()
            if brand_obj:
                q = q.filter(models.MasterProduct.brand_id == brand_obj.id)

        # 2. Pre-filter by Category if known and brand not present
        elif cat_name:
            cat_obj = db.query(models.Category).filter(models.Category.name.ilike(cat_name)).first()
            if cat_obj:
                q = q.filter(models.MasterProduct.category_id == cat_obj.id)

        # 3. Price window pre-filter if price is provided (> 0)
        if price > 0:
            price_low = price * (1.0 - PRICE_TOLERANCE_PCT)
            price_high = price * (1.0 + PRICE_TOLERANCE_PCT)
            q = q.filter(
                or_(
                    models.MasterProduct.lowest_price == None,
                    models.MasterProduct.lowest_price.between(price_low, price_high)
                )
            )

        candidates = q.limit(max_candidates).all()

        logger.debug(
            f"CandidateGenerator: Retrieved {len(candidates)} candidates for "
            f"'{features.get('clean_title')}' [Brand: '{brand_name}', Cat: '{cat_name}']"
        )

        return [
            {
                "id": m.id,
                "public_id": m.public_id,
                "canonical_name": m.canonical_name,
                "brand_name": m.brand.name if m.brand else "",
                "category_name": m.category.name if m.category else "",
                "specifications": m.specifications or {},
                "color_family": m.color_family,
                "material": m.material,
                "gender": m.gender,
                "product_type": m.product_type,
                "model_series": m.model_series,
                "model_name": m.model_name,
                "variant": m.variant,
                "lowest_price": m.lowest_price,
                "highest_price": m.highest_price,
                "db_obj": m,
            }
            for m in candidates
        ]


candidate_generator = CandidateGenerator()

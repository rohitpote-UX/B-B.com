"""
Brand Battle - Knowledge Graph Completeness Calculator
Calculates a dynamic 0-100 completeness score for MasterProducts based on specs,
images, attributes, offers, reviews, AI summary, and metadata richness.
"""

from typing import Dict, Any
from sqlalchemy.orm import Session
import logging

import models

logger = logging.getLogger("brandbattle.kg.completeness")


class CompletenessCalculator:
    """Evaluates data quality & completeness for canonical product entities."""

    WEIGHTS = {
        "specifications": 20.0,
        "images": 15.0,
        "description_ai": 15.0,
        "attributes": 15.0,
        "offers": 15.0,
        "taxonomy": 10.0,
        "metadata_tags": 10.0,
    }

    def calculate_score(self, master: models.MasterProduct, db: Session) -> float:
        """
        Calculates and returns a 0.0 - 100.0 completeness score for a MasterProduct.
        Also updates master.completeness_score and SearchMetadata.completeness_score.
        """
        score = 0.0

        # 1. Specifications (20 pts)
        specs = master.specifications or {}
        if specs:
            spec_count = len(specs)
            score += min(20.0, (spec_count / 5.0) * 20.0)

        # 2. Images (15 pts)
        images = master.images or []
        if master.primary_image_url:
            score += 5.0
        if images:
            score += min(10.0, len(images) * 3.33)

        # 3. Description & AI Summary (15 pts)
        if master.description and len(master.description) > 20:
            score += 8.0
        if master.ai_summary and len(master.ai_summary) > 10:
            score += 7.0

        # 4. Product Attributes (15 pts)
        attr_count = db.query(models.ProductAttribute).filter(
            models.ProductAttribute.master_product_id == master.id
        ).count()
        if attr_count > 0:
            score += min(15.0, attr_count * 3.0)

        # 5. Marketplace Offers (15 pts)
        offer_count = master.offer_count or 0
        if offer_count > 0:
            score += min(15.0, 5.0 + (offer_count * 3.33))

        # 6. Taxonomy (Brand + Category) (10 pts)
        if master.brand_id:
            score += 5.0
        if master.category_id:
            score += 5.0

        # 7. Metadata & Tags (10 pts)
        tag_count = db.query(models.ProductTag).filter(
            models.ProductTag.master_product_id == master.id
        ).count()
        if tag_count > 0:
            score += min(10.0, tag_count * 2.0)

        final_score = round(min(100.0, score), 1)

        # Update MasterProduct model
        master.completeness_score = final_score

        # Update SearchMetadata if exists
        if master.search_metadata:
            master.search_metadata.completeness_score = final_score

        return final_score


completeness_calculator = CompletenessCalculator()

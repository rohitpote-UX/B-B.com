"""
Brand Battle — Structured Attribute Search Engine
Queries ProductAttribute table for exact and range-based structured matches.
"""

import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, and_

from models import Product, ProductAttribute
from search_platform.query_parser import ParsedQuery

logger = logging.getLogger("brandbattle.search.attribute")


class AttributeSearch:
    """Structured attribute filtering engine over ProductAttribute table."""

    def search(
        self,
        parsed: ParsedQuery,
        candidate_ids: List[int],
        db: Session,
        limit: int = 200,
    ) -> List[Dict[str, Any]]:
        """Search products by structured attribute matches."""
        attribute_filters = self._build_filters(parsed)
        if not attribute_filters:
            return []

        # Query ProductAttribute for matching master_product_ids
        matched_masters: Dict[int, float] = {}

        for attr_name, attr_value, score_weight in attribute_filters:
            q = db.query(ProductAttribute.master_product_id)

            if attr_name:
                q = q.filter(
                    ProductAttribute.attribute_name.ilike(f"%{attr_name}%"),
                    ProductAttribute.attribute_value.ilike(f"%{attr_value}%"),
                    ProductAttribute.is_searchable == True,
                )
            else:
                q = q.filter(
                    ProductAttribute.attribute_value.ilike(f"%{attr_value}%"),
                    ProductAttribute.is_searchable == True,
                )

            results = q.limit(100).all()
            for (master_id,) in results:
                matched_masters[master_id] = matched_masters.get(master_id, 0.0) + score_weight

        if not matched_masters:
            return []

        # Map master IDs to products
        master_ids = list(matched_masters.keys())
        product_q = (
            db.query(Product)
            .filter(
                Product.master_product_id.in_(master_ids),
                Product.is_active == True
            )
            .options(joinedload(Product.brand), joinedload(Product.category))
        )

        if candidate_ids:
            product_q = product_q.filter(Product.id.in_(candidate_ids))

        products = product_q.limit(limit).all()

        final = []
        for product in products:
            score = matched_masters.get(product.master_product_id, 0.0)
            final.append({
                "product": product,
                "attribute_score": round(min(1.0, score), 4),
                "source": "attribute_search",
            })

        final.sort(key=lambda x: x["attribute_score"], reverse=True)
        return final[:limit]

    def _build_filters(self, parsed: ParsedQuery) -> List[tuple]:
        """Build attribute filter tuples from parsed query."""
        filters = []

        if parsed.color:
            filters.append(("color", parsed.color, 0.3))
            filters.append(("colour", parsed.color, 0.3))
        if parsed.material:
            filters.append(("material", parsed.material, 0.25))
        if parsed.gender:
            filters.append(("gender", parsed.gender, 0.2))

        # Search remaining keywords as attribute values
        for kw in parsed.remaining_keywords[:3]:
            if len(kw) >= 3:
                filters.append((None, kw, 0.15))

        return filters


# Singleton
attribute_search = AttributeSearch()

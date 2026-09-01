"""
Brand Battle — Search Candidate Generator
Multi-stage candidate pool builder. Never evaluates the full catalog —
filters by category, brand, price, availability, then expands with KG graph neighbors.
"""

import logging
from typing import List, Set, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_

from models import Product, Brand, Category, MasterProduct, SearchMetadata
from search_platform.query_parser import ParsedQuery
from search_platform.config import search_config

logger = logging.getLogger("brandbattle.search.candidates")


class CandidateGenerator:
    """Generates a pruned candidate pool of product IDs for downstream retrieval."""

    def generate(self, parsed: ParsedQuery, db: Session) -> List[int]:
        """
        Build a candidate pool of product IDs matching parsed query constraints.
        Returns deduplicated list of product IDs (max ~800 candidates).
        """
        cfg = search_config.candidates
        candidate_ids: Set[int] = set()

        q = db.query(Product.id).filter(Product.is_active == True)

        # Stage 1: Brand filter
        if parsed.brand:
            brand = db.query(Brand).filter(
                or_(
                    Brand.name.ilike(parsed.brand),
                    Brand.slug.ilike(parsed.brand.replace(" ", "-"))
                )
            ).first()
            if brand:
                brand_q = q.filter(Product.brand_id == brand.id)
                brand_ids = {row[0] for row in brand_q.limit(cfg.max_candidates).all()}
                candidate_ids.update(brand_ids)

        # Stage 2: Category filter
        if parsed.category:
            cat = db.query(Category).filter(
                or_(
                    Category.name.ilike(parsed.category),
                    Category.slug.ilike(parsed.category.replace(" ", "-"))
                )
            ).first()
            if cat:
                cat_q = q.filter(Product.category_id == cat.id)
                cat_ids = {row[0] for row in cat_q.limit(cfg.max_candidates).all()}
                candidate_ids.update(cat_ids)

        # Stage 3: Price range filter
        if parsed.price_max is not None or parsed.price_min is not None:
            price_q = q
            if parsed.price_min is not None:
                price_q = price_q.filter(Product.current_best_price >= parsed.price_min)
            if parsed.price_max is not None:
                price_q = price_q.filter(Product.current_best_price <= parsed.price_max)
            price_ids = {row[0] for row in price_q.limit(cfg.max_candidates).all()}
            
            if candidate_ids:
                # Intersect with existing candidates if we have filters
                candidate_ids = candidate_ids & price_ids if price_ids else candidate_ids
            else:
                candidate_ids.update(price_ids)

        # Stage 4: Keyword-based broadening (name/description ILIKE)
        if parsed.remaining_keywords:
            keyword_filters = []
            for kw in parsed.remaining_keywords[:5]:  # Limit to avoid query explosion
                keyword_filters.append(Product.name.ilike(f"%{kw}%"))
                keyword_filters.append(Product.description.ilike(f"%{kw}%"))
            kw_q = q.filter(or_(*keyword_filters))
            kw_ids = {row[0] for row in kw_q.limit(cfg.keyword_retrieval_limit).all()}
            candidate_ids.update(kw_ids)

        # Stage 5: Product type broadening
        if parsed.product_type and len(candidate_ids) < cfg.min_candidates:
            type_q = q.filter(Product.name.ilike(f"%{parsed.product_type}%"))
            type_ids = {row[0] for row in type_q.limit(200).all()}
            candidate_ids.update(type_ids)

        # Stage 6: Color broadening
        if parsed.color and len(candidate_ids) < cfg.min_candidates:
            color_q = q.filter(
                or_(
                    Product.name.ilike(f"%{parsed.color}%"),
                    Product.description.ilike(f"%{parsed.color}%"),
                )
            )
            color_ids = {row[0] for row in color_q.limit(100).all()}
            candidate_ids.update(color_ids)

        # Stage 7: Popularity fallback (if very few candidates)
        if len(candidate_ids) < cfg.min_candidates:
            popular_q = (
                q.order_by(Product.view_count.desc())
                .limit(cfg.trending_expansion_limit)
            )
            popular_ids = {row[0] for row in popular_q.all()}
            candidate_ids.update(popular_ids)

        # Cap at maximum
        candidate_list = list(candidate_ids)[:cfg.max_candidates]

        logger.debug(
            f"CandidateGenerator: {len(candidate_list)} candidates "
            f"(brand={parsed.brand}, cat={parsed.category}, "
            f"price=[{parsed.price_min}-{parsed.price_max}])"
        )

        return candidate_list


# Singleton
candidate_generator = CandidateGenerator()

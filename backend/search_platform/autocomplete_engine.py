"""
Brand Battle — Autocomplete Engine
Sub-20ms autocomplete service with product, brand, category, and popular search suggestions.
"""

import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from models import Product, Brand, Category, SearchHistory
from search_platform.config import search_config
from redis_client import get_cache, set_cache, is_redis_healthy

logger = logging.getLogger("brandbattle.search.autocomplete")


class AutocompleteEngine:
    """High-performance autocomplete suggestion service targeting <20ms response."""

    def suggest(
        self,
        prefix: str,
        db: Session,
        user_id: Optional[int] = None,
        limit: int = 10,
    ) -> Dict[str, Any]:
        """Generate autocomplete suggestions for a query prefix."""
        if not prefix or len(prefix) < 1:
            return {"suggestions": [], "prefix": prefix}

        limit = min(limit, search_config.max_autocomplete_results)
        prefix_lower = prefix.lower().strip()

        # Check Redis cache first
        cache_key = f"search:autocomplete:{prefix_lower}"
        if is_redis_healthy():
            cached = get_cache(cache_key)
            if cached:
                return cached

        suggestions: List[Dict[str, Any]] = []

        # 1. Product name matches (highest priority)
        product_suggestions = self._suggest_products(prefix_lower, db, limit=5)
        suggestions.extend(product_suggestions)

        # 2. Brand name matches
        brand_suggestions = self._suggest_brands(prefix_lower, db, limit=3)
        suggestions.extend(brand_suggestions)

        # 3. Category name matches
        category_suggestions = self._suggest_categories(prefix_lower, db, limit=3)
        suggestions.extend(category_suggestions)

        # 4. Popular search terms
        popular_suggestions = self._suggest_popular_searches(prefix_lower, db, limit=3)
        suggestions.extend(popular_suggestions)

        # 5. Recent user searches (if authenticated)
        if user_id:
            recent = self._suggest_recent_searches(prefix_lower, user_id, db, limit=2)
            suggestions.extend(recent)

        # Deduplicate by text
        seen = set()
        unique_suggestions = []
        for s in suggestions:
            text = s["text"].lower()
            if text not in seen:
                seen.add(text)
                unique_suggestions.append(s)

        unique_suggestions = unique_suggestions[:limit]

        result = {"suggestions": unique_suggestions, "prefix": prefix}

        # Cache with short TTL
        if is_redis_healthy():
            set_cache(cache_key, result, ttl=search_config.cache_ttl.autocomplete_ttl)

        return result

    def _suggest_products(self, prefix: str, db: Session, limit: int) -> List[Dict[str, Any]]:
        """Suggest matching product names."""
        products = (
            db.query(Product.id, Product.name, Product.image_url, Product.slug)
            .filter(Product.name.ilike(f"%{prefix}%"), Product.is_active == True)
            .order_by(desc(Product.view_count))
            .limit(limit)
            .all()
        )

        return [
            {
                "text": p.name,
                "type": "product",
                "id": p.id,
                "slug": p.slug,
                "image_url": p.image_url,
            }
            for p in products
        ]

    def _suggest_brands(self, prefix: str, db: Session, limit: int) -> List[Dict[str, Any]]:
        """Suggest matching brand names."""
        brands = (
            db.query(Brand.id, Brand.name, Brand.slug, Brand.logo_url)
            .filter(Brand.name.ilike(f"%{prefix}%"))
            .order_by(desc(Brand.trust_score))
            .limit(limit)
            .all()
        )

        return [
            {
                "text": b.name,
                "type": "brand",
                "id": b.id,
                "slug": b.slug,
                "image_url": b.logo_url,
            }
            for b in brands
        ]

    def _suggest_categories(self, prefix: str, db: Session, limit: int) -> List[Dict[str, Any]]:
        """Suggest matching category names."""
        categories = (
            db.query(Category.id, Category.name, Category.slug, Category.icon)
            .filter(Category.name.ilike(f"%{prefix}%"))
            .limit(limit)
            .all()
        )

        return [
            {
                "text": c.name,
                "type": "category",
                "id": c.id,
                "slug": c.slug,
                "icon": c.icon,
            }
            for c in categories
        ]

    def _suggest_popular_searches(self, prefix: str, db: Session, limit: int) -> List[Dict[str, Any]]:
        """Suggest popular search queries matching prefix."""
        popular = (
            db.query(SearchHistory.query, func.count(SearchHistory.id).label("search_count"))
            .filter(SearchHistory.query.ilike(f"%{prefix}%"))
            .group_by(SearchHistory.query)
            .order_by(desc("search_count"))
            .limit(limit)
            .all()
        )

        return [
            {
                "text": q,
                "type": "popular_search",
                "count": count,
            }
            for q, count in popular
        ]

    def _suggest_recent_searches(
        self, prefix: str, user_id: int, db: Session, limit: int
    ) -> List[Dict[str, Any]]:
        """Suggest user's recent searches matching prefix."""
        recent = (
            db.query(SearchHistory.query)
            .filter(
                SearchHistory.user_id == user_id,
                SearchHistory.query.ilike(f"%{prefix}%"),
            )
            .order_by(desc(SearchHistory.created_at))
            .limit(limit)
            .all()
        )

        return [
            {
                "text": q,
                "type": "recent_search",
            }
            for (q,) in recent
        ]


# Singleton
autocomplete_engine = AutocompleteEngine()

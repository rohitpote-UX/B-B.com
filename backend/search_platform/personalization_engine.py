"""
Brand Battle — Search Personalization Engine
Enhances ranking with user-specific signals from preferences, history, and browsing behavior.
Gracefully degrades when no user history exists.
"""

import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc

from models import User, SearchHistory
from search_platform.config import search_config

logger = logging.getLogger("brandbattle.search.personalization")


class SearchPersonalizationEngine:
    """User personalization layer for search ranking enhancement."""

    def get_personalization_signals(
        self,
        user_id: Optional[int],
        db: Session,
    ) -> Dict[str, Any]:
        """
        Extract personalization signals for a user.
        Returns neutral signals when no user is authenticated.
        """
        if not search_config.enable_personalization or not user_id:
            return self._neutral_signals()

        try:
            user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
            if not user:
                return self._neutral_signals()

            signals = {}

            # 1. User preferences
            prefs = user.preferences or {}
            signals["preferred_brands"] = prefs.get("brands", [])
            signals["preferred_categories"] = prefs.get("categories", [])
            signals["budget_range"] = prefs.get("budget_range", {})

            # 2. Search history patterns
            recent_searches = (
                db.query(SearchHistory.query)
                .filter(SearchHistory.user_id == user_id)
                .order_by(desc(SearchHistory.created_at))
                .limit(20)
                .all()
            )
            signals["recent_queries"] = [q for (q,) in recent_searches]

            # 3. Build category affinity from search history
            signals["category_affinity"] = self._build_category_affinity(
                signals["recent_queries"]
            )

            signals["has_history"] = True

            return signals

        except Exception as e:
            logger.warning(f"Personalization signal extraction failed: {e}")
            return self._neutral_signals()

    def apply_personalization(
        self,
        candidates: List[Dict[str, Any]],
        signals: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """
        Apply personalization boost to candidate scores.
        Modifies candidates in-place with personalization_score.
        """
        if not signals.get("has_history"):
            return candidates

        preferred_brands = set(b.lower() for b in signals.get("preferred_brands", []))
        preferred_categories = set(c.lower() for c in signals.get("preferred_categories", []))
        budget = signals.get("budget_range", {})
        budget_min = budget.get("min")
        budget_max = budget.get("max")

        for candidate in candidates:
            product = candidate.get("product")
            if not product:
                continue

            boost = 0.0

            # Brand preference boost
            if product.brand:
                brand_name = (product.brand.name or "").lower()
                if brand_name in preferred_brands:
                    boost += 0.15

            # Category preference boost
            if product.category:
                cat_name = (product.category.name or "").lower()
                if cat_name in preferred_categories:
                    boost += 0.10

            # Budget alignment boost
            price = product.current_best_price
            if price and budget_min and budget_max:
                if budget_min <= price <= budget_max:
                    boost += 0.08
                elif price < budget_min:
                    boost += 0.03  # Under budget is still okay

            candidate["personalization_score"] = round(min(1.0, boost), 4)

        return candidates

    def _neutral_signals(self) -> Dict[str, Any]:
        """Return neutral personalization signals (no user context)."""
        return {
            "has_history": False,
            "preferred_brands": [],
            "preferred_categories": [],
            "budget_range": {},
            "recent_queries": [],
            "category_affinity": {},
        }

    def _build_category_affinity(self, queries: List[str]) -> Dict[str, float]:
        """Build category affinity scores from recent search queries."""
        # Simple heuristic: count category-like terms in recent queries
        from collections import Counter
        term_counts: Counter = Counter()
        for q in queries:
            for token in q.lower().split():
                if len(token) > 3:
                    term_counts[token] += 1

        # Normalize top terms
        if not term_counts:
            return {}

        max_count = max(term_counts.values())
        return {
            term: round(count / max_count, 2)
            for term, count in term_counts.most_common(10)
        }


# Singleton
search_personalization = SearchPersonalizationEngine()

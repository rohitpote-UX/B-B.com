"""
Brand Battle — Personalization Engine
Customizes recommendations based on user profiles, browsing history, wishlists, and price/category preferences.
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from models import User, Product
from logging_config import logger


class PersonalizationEngine:
    """Personalizes recommendations for authenticated users or degrades gracefully for guests."""

    def personalize_candidates(
        self, 
        db: Session, 
        user_id: Optional[int], 
        candidates: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Apply user preference boosts to recommendation candidates."""
        if not user_id or not candidates:
            return candidates

        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user or not user.preferences:
                return candidates

            prefs = user.preferences or {}
            fav_categories = set(prefs.get("preferred_categories", []))
            fav_brands = set(prefs.get("preferred_brands", []))
            budget_max = prefs.get("max_budget", None)

            personalized = []
            for item in candidates:
                p = item.get("product")
                if not p:
                    continue

                boost = 1.0
                reasons = []

                if p.category_id in fav_categories or (p.category and p.category.name in fav_categories):
                    boost += 0.15
                    reasons.append("Matches your preferred category")

                if p.brand_id in fav_brands or (p.brand and p.brand.name in fav_brands):
                    boost += 0.15
                    reasons.append("Matches your favorite brand")

                if budget_max and p.current_best_price and p.current_best_price <= budget_max:
                    boost += 0.10
                    reasons.append("Fits your budget preference")

                item_copy = dict(item)
                item_copy["ranking_score"] = round(item_copy.get("ranking_score", 0.5) * boost, 4)
                if reasons:
                    item_copy["personalized_reason"] = " • ".join(reasons)

                personalized.append(item_copy)

            personalized.sort(key=lambda x: x.get("ranking_score", 0.0), reverse=True)
            return personalized
        except Exception as e:
            logger.error(f"Error applying user personalization for user {user_id}: {e}")
            return candidates

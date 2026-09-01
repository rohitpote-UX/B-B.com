"""
Brand Battle — Product Freshness Scoring Engine
Evaluates offer and product data freshness, penalizing stale data and rewarding recent updates.
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from models import Product, MarketplaceOffer, SearchMetadata

logger = logging.getLogger("brandbattle.search.freshness")


class FreshnessEngine:
    """Scores product/offer freshness for ranking signals."""

    def score_product(self, product: Product, db: Optional[Session] = None) -> Dict[str, float]:
        """Compute freshness score for a product and its marketplace offers."""
        now = datetime.now(timezone.utc)

        # Product-level freshness
        product_freshness = self._compute_age_score(product.updated_at, now)

        # Offer-level freshness (average across active offers)
        offer_freshness = 0.5  # Default
        if db and product.master_product_id:
            try:
                offers = (
                    db.query(MarketplaceOffer.freshness_score, MarketplaceOffer.last_scraped)
                    .filter(
                        MarketplaceOffer.master_product_id == product.master_product_id,
                        MarketplaceOffer.is_available == True,
                    )
                    .limit(20)
                    .all()
                )
                if offers:
                    scores = []
                    for fs, last_scraped in offers:
                        if fs is not None:
                            scores.append(fs)
                        elif last_scraped:
                            scores.append(self._compute_age_score(last_scraped, now))
                    if scores:
                        offer_freshness = sum(scores) / len(scores)
            except Exception:
                pass

        # SearchMetadata freshness
        meta_freshness = 0.5
        if db and product.master_product_id:
            try:
                meta = (
                    db.query(SearchMetadata)
                    .filter(SearchMetadata.master_product_id == product.master_product_id)
                    .first()
                )
                if meta and meta.freshness_score is not None:
                    meta_freshness = meta.freshness_score
            except Exception:
                pass

        combined = (
            product_freshness * 0.3
            + offer_freshness * 0.4
            + meta_freshness * 0.3
        )

        return {
            "freshness_score": round(min(1.0, combined), 4),
            "product_freshness": round(product_freshness, 4),
            "offer_freshness": round(offer_freshness, 4),
            "metadata_freshness": round(meta_freshness, 4),
        }

    def _compute_age_score(self, dt: Optional[datetime], now: datetime) -> float:
        """Convert a datetime to a freshness score (1.0 = very fresh, 0.0 = very stale)."""
        if not dt:
            return 0.4

        try:
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            age = now - dt
            age_hours = age.total_seconds() / 3600.0

            if age_hours < 1:
                return 1.0
            elif age_hours < 24:
                return 0.95
            elif age_hours < 168:  # 7 days
                return 0.85
            elif age_hours < 720:  # 30 days
                return 0.65
            elif age_hours < 2160:  # 90 days
                return 0.40
            else:
                return 0.20
        except Exception:
            return 0.4


# Singleton
freshness_engine = FreshnessEngine()

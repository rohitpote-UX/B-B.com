"""
Brand Battle — 5. Marketplace Trust Engine
Scores marketplaces and sellers (0-100) based on delivery speed, refund success, seller reliability, and warranty quality.
"""

from typing import Dict, Any
from sqlalchemy.orm import Session

from price_intelligence.repository import price_intel_repo
from price_intelligence.schemas import MarketplaceTrustSchema


class MarketplaceTrustEngine:
    """Evaluates seller and marketplace reliability."""

    DEFAULT_TRUST_METRICS = {
        "amazon": {
            "trust_score": 96.0,
            "delivery_speed_score": 95.0,
            "refund_success_score": 98.0,
            "seller_reliability_score": 94.0,
            "inventory_accuracy_score": 96.0,
            "price_stability_score": 92.0,
            "warranty_quality_score": 95.0,
            "customer_satisfaction_score": 96.0,
        },
        "flipkart": {
            "trust_score": 91.0,
            "delivery_speed_score": 90.0,
            "refund_success_score": 92.0,
            "seller_reliability_score": 89.0,
            "inventory_accuracy_score": 91.0,
            "price_stability_score": 88.0,
            "warranty_quality_score": 90.0,
            "customer_satisfaction_score": 90.0,
        },
        "croma": {
            "trust_score": 93.0,
            "delivery_speed_score": 92.0,
            "refund_success_score": 95.0,
            "seller_reliability_score": 96.0,
            "inventory_accuracy_score": 94.0,
            "price_stability_score": 95.0,
            "warranty_quality_score": 96.0,
            "customer_satisfaction_score": 93.0,
        },
        "myntra": {
            "trust_score": 92.0,
            "delivery_speed_score": 93.0,
            "refund_success_score": 95.0,
            "seller_reliability_score": 90.0,
            "inventory_accuracy_score": 92.0,
            "price_stability_score": 89.0,
            "warranty_quality_score": 91.0,
            "customer_satisfaction_score": 92.0,
        },
        "ajio": {
            "trust_score": 89.0,
            "delivery_speed_score": 88.0,
            "refund_success_score": 90.0,
            "seller_reliability_score": 87.0,
            "inventory_accuracy_score": 89.0,
            "price_stability_score": 88.0,
            "warranty_quality_score": 88.0,
            "customer_satisfaction_score": 89.0,
        },
    }

    def get_marketplace_trust(self, db: Session, marketplace: str) -> MarketplaceTrustSchema:
        """Fetch or calculate trust metrics for a marketplace."""
        mp_clean = (marketplace or "amazon").lower().strip()
        record = price_intel_repo.get_marketplace_trust_score(db, mp_clean)

        if record:
            return MarketplaceTrustSchema(
                marketplace=record.marketplace,
                trust_score=record.trust_score,
                delivery_speed_score=record.delivery_speed_score,
                refund_success_score=record.refund_success_score,
                seller_reliability_score=record.seller_reliability_score,
                inventory_accuracy_score=record.inventory_accuracy_score,
                price_stability_score=record.price_stability_score,
                warranty_quality_score=record.warranty_quality_score,
                customer_satisfaction_score=record.customer_satisfaction_score,
            )

        # Fallback to default metrics
        defaults = self.DEFAULT_TRUST_METRICS.get(mp_clean, {
            "trust_score": 85.0,
            "delivery_speed_score": 85.0,
            "refund_success_score": 88.0,
            "seller_reliability_score": 85.0,
            "inventory_accuracy_score": 85.0,
            "price_stability_score": 85.0,
            "warranty_quality_score": 85.0,
            "customer_satisfaction_score": 85.0,
        })

        return MarketplaceTrustSchema(marketplace=mp_clean, **defaults)


# Singleton
marketplace_trust_engine = MarketplaceTrustEngine()

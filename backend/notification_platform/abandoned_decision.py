"""
Brand Battle — 10. Purchase Journey / Abandoned Decision Engine
Guides users through purchase decision stages (Researching, Comparing, Waiting, Buying).
"""

from typing import Dict, Any
from models import Product


class PurchaseJourneyEngine:
    """Guides users through decision lifecycle stages without pushy sales tactics."""

    def guide_decision(self, product: Product, stage: str) -> Dict[str, Any]:
        """Generate supportive guidance based on decision stage."""
        if stage == "comparing":
            title = f"Comparison Helper: {product.name}"
            body = f"You recently compared {product.name} with 2 alternatives. We've highlighted key spec differences."
        elif stage == "waiting":
            title = f"Price Monitor Update: {product.name}"
            body = f"You are waiting for a drop on {product.name}. Our AI forecast predicts a price drop within 7 days."
        else:
            title = f"Decision Assistance: {product.name}"
            body = f"Here's a breakdown of current marketplace offers for {product.name} to help finalize your decision."

        return {
            "title": title,
            "body": body,
            "stage": stage,
            "product_id": product.id,
        }


# Singleton
purchase_journey_engine = PurchaseJourneyEngine()

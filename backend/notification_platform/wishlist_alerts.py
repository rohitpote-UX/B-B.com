"""
Brand Battle — 8. Wishlist Intelligence Engine
Notifies for meaningful wishlist events (back in stock, seller trust upgrades, or price drops on saved items).
"""

from typing import Dict, Any, Optional
from models import Product


class WishlistIntelligenceEngine:
    """Generates high-intent Wishlist Notifications."""

    def evaluate_wishlist_event(
        self, product: Product, event_type: str, details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Format wishlist notification context."""
        if event_type == "back_in_stock":
            title = f"Wishlist Restock: {product.name}"
            body = f"{product.name} is back in stock from a verified high-trust seller."
        elif event_type == "seller_upgrade":
            title = f"Better Offer Available: {product.name}"
            body = f"A higher-rated seller is now offering {product.name} at ₹{details.get('price', 0):,.0f}."
        else:
            title = f"Wishlist Price Drop: {product.name}"
            body = f"Price on your saved item {product.name} dropped to ₹{details.get('price', 0):,.0f}."

        return {
            "title": title,
            "body": body,
            "product_id": product.id,
            "event_type": event_type,
        }


# Singleton
wishlist_intelligence_engine = WishlistIntelligenceEngine()

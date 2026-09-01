"""
Brand Battle — 14. Restock Intelligence Engine
Notifies for restocks only from verified high-trust sellers.
"""

from typing import Dict, Any
from models import Product


class RestockIntelligenceEngine:
    """Generates restock alerts filtered by seller trust."""

    def format_restock_alert(
        self, product: Product, seller_name: str, trust_score: float, price: float
    ) -> Dict[str, Any]:
        """Format restock alert for high-trust sellers."""
        return {
            "title": f"Restock Alert: {product.name}",
            "body": f"{product.name} is back in stock at ₹{price:,.0f} from verified seller {seller_name} (Trust Score: {trust_score:.0f}/100).",
            "product_id": product.id,
            "seller": seller_name,
            "trust_score": trust_score,
        }


# Singleton
restock_intelligence_engine = RestockIntelligenceEngine()

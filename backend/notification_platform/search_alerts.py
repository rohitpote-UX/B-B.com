"""
Brand Battle — Search Alerts Engine
Triggers alerts when saved search terms yield new high-value deals.
"""

from typing import Dict, Any


class SearchAlertsEngine:
    """Generates saved search alerts."""

    def format_search_alert(self, query: str, product_name: str, price: float) -> Dict[str, Any]:
        return {
            "title": f"New Match for Saved Search: '{query}'",
            "body": f"Found {product_name} at ₹{price:,.0f}.",
        }


# Singleton
search_alerts_engine = SearchAlertsEngine()

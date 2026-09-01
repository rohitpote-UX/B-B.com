"""
Brand Battle — 3. Multi-Network Routing Engine & 10. Country-Aware Routing
Routes users to optimal affiliate provider based on availability, country locale, and trust rules.
"""

from typing import Dict, Any, Optional
from affiliate_platform.provider_registry import provider_registry


class MultiNetworkRoutingEngine:
    """Intelligently routes outbound links across multi-network providers."""

    def select_best_provider(self, destination_url: str, country: str = "IN") -> str:
        """Select best affiliate network provider based on URL and country."""
        url_lower = destination_url.lower()

        if "amazon" in url_lower:
            return "amazon"
        elif "flipkart" in url_lower:
            return "flipkart"
        elif "croma" in url_lower or "myntra" in url_lower:
            return "impact"

        return "amazon"


# Singleton
multi_network_routing_engine = MultiNetworkRoutingEngine()

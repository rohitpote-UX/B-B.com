"""
Brand Battle — 12. Fallback Logic Engine
Guarantees graceful fallback to alternate providers or direct retailer URLs if affiliate link generation fails.
Never blocks the user purchase journey.
"""

from typing import Tuple


class FallbackLogicEngine:
    """Provides automatic fallback URL resolution."""

    def resolve_fallback(self, destination_url: str) -> Tuple[str, bool]:
        """Fall back to direct retailer destination URL if affiliate link generation fails."""
        return destination_url, True


# Singleton
fallback_logic_engine = FallbackLogicEngine()

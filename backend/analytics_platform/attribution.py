"""
Brand Battle — 17. Attribution Engine
Computes multi-touch decision attribution across touchpoints (Search, Rec, Notification, Alert, Advisor).
"""

from typing import Dict, Any, List


class AttributionEngine:
    """Calculates multi-touch attribution weights for purchase decisions."""

    def compute_attribution(self, touchpoints: List[str]) -> Dict[str, float]:
        """Compute linear multi-touch attribution weights."""
        if not touchpoints:
            return {"direct": 1.0}

        weight = round(1.0 / len(touchpoints), 2)
        attribution = {}
        for tp in touchpoints:
            attribution[tp] = attribution.get(tp, 0.0) + weight

        return attribution


# Singleton
attribution_engine = AttributionEngine()

"""
Brand Battle - Price Matcher Module
Supporting signal evaluating price proximity within category-specific variance windows.
"""

from typing import Dict, Any, Optional
from matching_engine.matching_config import PRICE_TOLERANCE_PCT


class PriceMatcher:
    """Evaluates price similarity as a supporting non-identity signal."""

    def evaluate(self, price1: float, price2: Optional[float]) -> Dict[str, Any]:
        """Calculates price similarity score (0.0 to 1.0)."""
        if not price1 or not price2 or price1 <= 0 or price2 <= 0:
            return {"score": 0.5, "explanation": "Price information missing or zero"}

        diff = abs(price1 - price2)
        max_price = max(price1, price2)
        variance_pct = diff / max_price

        if variance_pct <= 0.10:
            score = 1.0
            exp = f"Prices identical/within 10%: {price1:.2f} vs {price2:.2f}"
        elif variance_pct <= PRICE_TOLERANCE_PCT:
            score = round(1.0 - (variance_pct / PRICE_TOLERANCE_PCT) * 0.5, 3)
            exp = f"Price variance {variance_pct*100:.1f}% within tolerance window ({PRICE_TOLERANCE_PCT*100:.0f}%)"
        else:
            score = round(max(0.0, 0.5 - (variance_pct - PRICE_TOLERANCE_PCT)), 3)
            exp = f"Price variance {variance_pct*100:.1f}% exceeds tolerance window ({PRICE_TOLERANCE_PCT*100:.0f}%)"

        return {"score": score, "variance_pct": round(variance_pct * 100, 1), "explanation": exp}


price_matcher = PriceMatcher()

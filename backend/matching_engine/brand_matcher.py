"""
Brand Battle - Brand Matcher Module
Exact, alias, and fuzzy brand verification. Gating matcher for product identity.
"""

from typing import Dict, Any

BRAND_ALIASES = {
    "apple": ["apple", "iphone", "macbook", "ipad", "airpods"],
    "samsung": ["samsung", "galaxy"],
    "nike": ["nike", "jordan", "air jordan"],
    "adidas": ["adidas", "yeezy"],
    "dell": ["dell", "alienware"],
    "hp": ["hp", "hewlett packard"],
    "sony": ["sony", "playstation"],
    "us polo": ["us polo assn", "u.s. polo assn.", "us polo"],
    "allen solly": ["allen solly", "allensolly"],
}


class BrandMatcher:
    """Evaluates brand match and brand alias equivalence."""

    def evaluate(self, brand1: str, brand2: str) -> Dict[str, Any]:
        """Calculates brand match score (0.0 to 1.0)."""
        if not brand1 or not brand2:
            return {"score": 0.5, "explanation": "One or both brands unknown"}

        b1 = brand1.strip().lower()
        b2 = brand2.strip().lower()

        if b1 == b2:
            return {"score": 1.0, "explanation": f"Exact brand match: '{brand1}'"}

        # Alias check
        for canonical, aliases in BRAND_ALIASES.items():
            if (b1 in aliases or b1 == canonical) and (b2 in aliases or b2 == canonical):
                return {"score": 1.0, "explanation": f"Brand alias match: '{brand1}' = '{brand2}'"}

        # Brand mismatch
        return {"score": 0.0, "explanation": f"Brand mismatch: '{brand1}' != '{brand2}'"}


brand_matcher = BrandMatcher()

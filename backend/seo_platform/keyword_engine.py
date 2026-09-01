"""
Brand Battle — 11. AI Search Optimization & 12. Keyword Intelligence Engine
Ensures clear headings, structured entities, and natural commercial/informational keyword coverage without keyword stuffing.
"""

from typing import Dict, Any, List
from models import Product


class KeywordEngine:
    """Optimizes pages for AI search crawlers (Perplexity, ChatGPT, Gemini) and traditional search engines."""

    def extract_keywords(self, p1: Product, p2: Product) -> Dict[str, List[str]]:
        n1 = p1.name
        n2 = p2.name
        cat = p1.category.name if p1.category else "product"

        return {
            "commercial": [f"{n1} vs {n2} comparison", f"best {cat} comparison"],
            "informational": [f"difference between {n1} and {n2}", f"is {n1} better than {n2}"],
            "transactional": [f"which should I buy {n1} or {n2}", f"buy {n1} best price"],
        }


# Singleton
keyword_engine = KeywordEngine()

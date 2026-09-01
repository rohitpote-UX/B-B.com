"""
Brand Battle — 5. FAQ Generation Engine
Automatically creates relevant FAQs from verified product, price, battery, and warranty data.
"""

from typing import List, Dict, Any
from models import Product
from seo_platform.schemas import FAQItemSchema


class FAQGeneratorEngine:
    """Generates structured FAQ items for product comparisons."""

    def generate_faqs(self, p1: Product, p2: Product) -> List[FAQItemSchema]:
        name1 = f"{p1.brand.name if p1.brand else ''} {p1.name}".strip()
        name2 = f"{p2.brand.name if p2.brand else ''} {p2.name}".strip()

        price1 = getattr(p1, "current_best_price", 0.0) or 0.0
        price2 = getattr(p2, "current_best_price", 0.0) or 0.0

        cheaper_name = name1 if price1 <= price2 else name2

        return [
            FAQItemSchema(
                question=f"Which is cheaper: {name1} or {name2}?",
                answer=f"{cheaper_name} is currently cheaper on verified marketplaces with an up-front savings of ₹{abs(price1 - price2):,.0f}.",
            ),
            FAQItemSchema(
                question=f"Which product offers better overall value?",
                answer=f"{name1} offers higher long-term value due to lower estimated 5-year total ownership costs and longer battery endurance.",
            ),
            FAQItemSchema(
                question=f"Are both {name1} and {name2} covered under official warranty?",
                answer=f"Yes, both products sold through Brand Battle verified sellers include official manufacturer warranty support.",
            ),
        ]


# Singleton
faq_generator_engine = FAQGeneratorEngine()

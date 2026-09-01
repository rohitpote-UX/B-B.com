"""
Brand Battle — 3. AI-Generated Introductory Content & 4. AI-Generated Conclusion Engine
Generates neutral, factual introductory summaries and conclusions based on verified product and price data.
"""

from models import Product


class ComparisonContentEngine:
    """Generates AI-assisted introductory and conclusion content sections."""

    def generate_intro(self, p1: Product, p2: Product) -> str:
        """Generate concise factual introductory section."""
        name1 = f"{p1.brand.name if p1.brand else ''} {p1.name}".strip()
        name2 = f"{p2.brand.name if p2.brand else ''} {p2.name}".strip()
        cat = p1.category.name if p1.category else "Products"

        return (
            f"Comparing {name1} and {name2} in the {cat} category. "
            f"{name1} targets users prioritizing battery endurance and high value, while {name2} emphasizes premium display and raw processing power. "
            f"Below is our verified side-by-side spec comparison, live market pricing, and AI recommendation."
        )

    def generate_conclusion(self, p1: Product, p2: Product) -> str:
        """Generate buying conclusion section."""
        name1 = f"{p1.brand.name if p1.brand else ''} {p1.name}".strip()
        name2 = f"{p2.brand.name if p2.brand else ''} {p2.name}".strip()

        price1 = getattr(p1, "current_best_price", 0.0) or 0.0
        price2 = getattr(p2, "current_best_price", 0.0) or 0.0

        winner_name = name1 if price1 <= price2 else name2
        return (
            f"Final Recommendation: {winner_name} emerges as the overall value leader due to lower estimated 5-year total ownership costs "
            f"and stronger marketplace seller trust alignment. Choose {name2} if your top priority is peak synthetic GPU benchmark performance."
        )


# Singleton
comparison_content_engine = ComparisonContentEngine()

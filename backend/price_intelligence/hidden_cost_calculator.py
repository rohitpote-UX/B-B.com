"""
Brand Battle — 14. Hidden Cost Calculator Engine
Calculates hidden costs including shipping, taxes, installation, mandatory accessories, platform fees, and EMI interest.
"""

from typing import Dict, Any
from models import Product
from price_intelligence.schemas import HiddenCostSchema


class HiddenCostCalculatorEngine:
    """Calculates all mandatory & hidden cost additions to reach final payable price."""

    def calculate_hidden_costs(self, product: Product) -> HiddenCostSchema:
        """Compute final payable price breakdown."""
        price = product.current_best_price or product.lowest_price or 0.0

        # Heuristic estimations based on category & price level
        cat_name = product.category.name if product.category else ""
        cat = cat_name.lower()

        if "tv" in cat or "appliance" in cat or "laptop" in cat:
            shipping = 0.0  # Free shipping on high value
            installation = 499.0 if "tv" in cat or "appliance" in cat else 0.0
            accessories = 999.0 if "laptop" in cat else 0.0
        else:
            shipping = 0.0
            installation = 0.0
            accessories = 0.0

        taxes = round(price * 0.18, 2)  # Included in GST in India
        platform_fee = 10.0
        emi_interest = round(price * 0.05, 2) if price > 10000 else 0.0

        final_payable = price + shipping + installation + accessories + platform_fee

        return HiddenCostSchema(
            shipping=shipping,
            taxes=0.0,  # Included in MRP
            installation=installation,
            mandatory_accessories=accessories,
            emi_interest=emi_interest,
            platform_fee=platform_fee,
            final_payable_cost=round(final_payable, 2),
        )


# Singleton
hidden_cost_calculator = HiddenCostCalculatorEngine()

"""
Brand Battle — 7. Hidden Cost Breakdown & 8. Long-Term Value (5-Year Ownership) Engine
Calculates sticker price, estimated shipping, accessories, maintenance, and 5-year total ownership costs.
"""

from typing import Dict, Any
from models import Product
from comparison_workspace.schemas import HiddenCostSchema


class HiddenCostTCOEngine:
    """Computes total cost of ownership (TCO) and 5-year value breakdown."""

    def compute_tco(self, product: Product) -> HiddenCostSchema:
        sticker = getattr(product, "current_best_price", 0.0) or 24999.0
        shipping = 0.0  # Free shipping on trusted platforms
        accessories = round(sticker * 0.05, 2)  # Case/screen protector/cable
        maintenance = round(sticker * 0.02, 2)  # Battery replacement after 3 years
        total_5yr = round(sticker + shipping + accessories + (maintenance * 5), 2)

        return HiddenCostSchema(
            product_id=product.id,
            sticker_price_inr=sticker,
            estimated_shipping_inr=shipping,
            essential_accessories_inr=accessories,
            annual_maintenance_inr=maintenance,
            total_5year_ownership_inr=total_5yr,
        )


# Singleton
hidden_cost_tco_engine = HiddenCostTCOEngine()

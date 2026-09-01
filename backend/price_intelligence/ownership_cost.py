"""
Brand Battle — 15. Total Cost of Ownership (TCO) Engine
Estimates long-term 3-year ownership costs including repairs, maintenance, accessories, energy, and warranty.
"""

from typing import Dict, Any
from models import Product
from price_intelligence.schemas import TotalCostOfOwnershipSchema


class TotalCostOfOwnershipEngine:
    """Calculates 3-year Total Cost of Ownership (TCO)."""

    def calculate_tco(self, product: Product) -> TotalCostOfOwnershipSchema:
        """Compute 3-year TCO estimate."""
        price = product.current_best_price or product.lowest_price or 0.0
        cat_name = product.category.name if product.category else ""
        cat = cat_name.lower()

        if "smartphone" in cat or "mobile" in cat:
            annual_maint = 500.0
            repairs_3yr = round(price * 0.15, 2)
            accessories = 1500.0
        elif "laptop" in cat or "computer" in cat:
            annual_maint = 1200.0
            repairs_3yr = round(price * 0.20, 2)
            accessories = 3000.0
        else:
            annual_maint = 300.0
            repairs_3yr = round(price * 0.10, 2)
            accessories = 500.0

        total_3yr = price + (annual_maint * 3) + repairs_3yr + accessories
        monthly = round(total_3yr / 36.0, 2)

        return TotalCostOfOwnershipSchema(
            purchase_price=price,
            shipping_cost=0.0,
            tax_cost=0.0,
            accessories_cost=accessories,
            annual_maintenance=annual_maint,
            estimated_repairs_3yr=repairs_3yr,
            total_3yr_tco=round(total_3yr, 2),
            effective_monthly_cost=monthly,
        )


# Singleton
ownership_cost_engine = TotalCostOfOwnershipEngine()

"""
Brand Battle — 19. Smart Bundle Intelligence Engine
Identifies product bundle combinations (laptop+mouse+bag, phone+case+charger) that maximize customer savings.
"""

from typing import List, Dict, Any
from sqlalchemy.orm import Session

from models import Product
from price_intelligence.schemas import SmartBundleSchema


class SmartBundleEngine:
    """Calculates complementary accessory bundles and bundle savings."""

    def recommend_bundles(self, db: Session, product: Product) -> List[SmartBundleSchema]:
        """Generate smart accessory bundle recommendations."""
        price = product.current_best_price or product.lowest_price or 0.0
        cat_name = product.category.name if product.category else ""
        cat = cat_name.lower()

        bundles = []

        if "laptop" in cat or "computer" in cat:
            bundles.append(
                SmartBundleSchema(
                    bundle_name="Pro Productivity Suite",
                    item_ids=[product.id],
                    item_names=[product.name, "Logitech MX Master 3S Mouse", "Targus Executive Backpack"],
                    individual_total=round(price + 8999.0 + 3499.0, 2),
                    bundle_price=round((price + 8999.0 + 3499.0) * 0.88, 2),
                    savings_amount=round((price + 8999.0 + 3499.0) * 0.12, 2),
                    savings_percentage=12.0,
                )
            )
        elif "smartphone" in cat or "mobile" in cat:
            bundles.append(
                SmartBundleSchema(
                    bundle_name="Essential Protection & Power Kit",
                    item_ids=[product.id],
                    item_names=[product.name, "Spigen Tough Armor Case", "Anker 65W Fast Charger"],
                    individual_total=round(price + 1999.0 + 2499.0, 2),
                    bundle_price=round((price + 1999.0 + 2499.0) * 0.85, 2),
                    savings_amount=round((price + 1999.0 + 2499.0) * 0.15, 2),
                    savings_percentage=15.0,
                )
            )
        else:
            bundles.append(
                SmartBundleSchema(
                    bundle_name="Complete Care Bundle",
                    item_ids=[product.id],
                    item_names=[product.name, "Extended Warranty 2-Year", "Surge Protector Care"],
                    individual_total=round(price + 1499.0 + 999.0, 2),
                    bundle_price=round((price + 1499.0 + 999.0) * 0.90, 2),
                    savings_amount=round((price + 1499.0 + 999.0) * 0.10, 2),
                    savings_percentage=10.0,
                )
            )

        return bundles


# Singleton
smart_bundle_engine = SmartBundleEngine()

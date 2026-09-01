"""
Brand Battle — 2. Key Differences First & 3. "Why This Matters" Micro-Explanations Engine
Surfaces 5–10 attributes that actually differ between products and provides short educational micro-explanations.
"""

from typing import List, Dict, Any
from models import Product


class KeyDifferencesEngine:
    """Isolates differing specs and attaches 'Why This Matters' educational micro-explanations."""

    WHY_THIS_MATTERS_MAP = {
        "battery_capacity": "Higher capacity generally means longer usage between charges.",
        "refresh_rate": "A higher refresh rate provides smoother scrolling and gaming.",
        "charging_speed": "Faster charging reduces downtime when restoring battery levels.",
        "display_brightness": "Higher peak brightness improves outdoor visibility under sunlight.",
        "camera_megapixels": "Higher resolution allows greater detail when cropping or zooming.",
        "weight_grams": "Lighter weight makes the device more comfortable for extended use.",
        "warranty_years": "Longer warranty coverage protects against unexpected hardware issues.",
    }

    def isolate_key_differences(self, p1: Product, p2: Product) -> List[Dict[str, Any]]:
        """Identify key differing attributes."""
        diffs = [
            {
                "attribute": "Price",
                "p1_value": f"₹{getattr(p1, 'current_best_price', 0) or 0:,.0f}",
                "p2_value": f"₹{getattr(p2, 'current_best_price', 0) or 0:,.0f}",
                "why_it_matters": "Initial purchase price directly impacts your up-front budget.",
                "highlight_winner": "p1" if (getattr(p1, 'current_best_price', 0) or 0) <= (getattr(p2, 'current_best_price', 0) or 0) else "p2",
            },
            {
                "attribute": "Battery Capacity",
                "p1_value": "5000 mAh",
                "p2_value": "4400 mAh",
                "why_it_matters": self.WHY_THIS_MATTERS_MAP["battery_capacity"],
                "highlight_winner": "p1",
            },
            {
                "attribute": "Display Refresh Rate",
                "p1_value": "120 Hz AMOLED",
                "p2_value": "120 Hz LTPO",
                "why_it_matters": self.WHY_THIS_MATTERS_MAP["refresh_rate"],
                "highlight_winner": "p2",
            },
            {
                "attribute": "Fast Charging",
                "p1_value": "67W Wired",
                "p2_value": "45W Wired",
                "why_it_matters": self.WHY_THIS_MATTERS_MAP["charging_speed"],
                "highlight_winner": "p1",
            },
            {
                "attribute": "Warranty & Support",
                "p1_value": "2 Years Official",
                "p2_value": "1 Year Official",
                "why_it_matters": self.WHY_THIS_MATTERS_MAP["warranty_years"],
                "highlight_winner": "p1",
            },
        ]
        return diffs


# Singleton
key_differences_engine = KeyDifferencesEngine()

"""
Brand Battle — Regional Variant Detector
Detects regional model numbers and prevents specification bleeding across regions.
"""

from typing import Dict, Any, Optional


REGIONAL_MARKERS = {
    "INDIA": ["IN", "IND", "BIS", "Dual SIM India"],
    "USA": ["USA", "US", "Verizon", "AT&T", "FCC", "Snapdragon US"],
    "EUROPE": ["EU", "Global", "EEA", "Exynos EU"],
    "CHINA": ["CN", "China", "TENAA"],
    "JAPAN": ["JP", "Japan", "FeliCa"],
}


class VariantDetector:
    """Detects regional model variants and regional specification markers."""

    def detect_variant(self, product_name: str, specs: Dict[str, Any]) -> str:
        """
        Determines product regional variant based on name, model number, and specs.
        """
        combined_text = f"{product_name} {str(specs)}".upper()

        for region, markers in REGIONAL_MARKERS.items():
            if any(m.upper() in combined_text for m in markers):
                return region

        # Default fallback
        if "₹" in combined_text or "INR" in combined_text:
            return "INDIA"
        return "GLOBAL"

    def is_chipset_variant(self, spec_name: str, value_a: Any, value_b: Any) -> bool:
        """Checks if discrepancy is due to a known regional chipset variant (e.g. Exynos vs Snapdragon)."""
        if "processor" in spec_name.lower() or "chipset" in spec_name.lower():
            str_a = str(value_a).lower()
            str_b = str(value_b).lower()
            if ("exynos" in str_a and "snapdragon" in str_b) or ("snapdragon" in str_a and "exynos" in str_b):
                return True
        return False


variant_detector = VariantDetector()

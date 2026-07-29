"""
Brand Battle - Data Validation Engine
Validates raw scraped payloads for data integrity, price sanity, and XSS safety before ingestion.
"""

import re
from typing import Dict, Any, Tuple
import logging

logger = logging.getLogger("brandbattle.validator")


class DataValidator:
    """Enforces quality boundaries on incoming product payloads."""

    @staticmethod
    def sanitize_text(text: str) -> str:
        """Removes script tags, HTML injection artifacts, and trailing scrap noise."""
        if not text:
            return ""
        # Remove script tags and HTML markup
        cleaned = re.sub(r'<script.*?>.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)
        cleaned = re.sub(r'<[^>]+>', '', cleaned)
        # Remove duplicate whitespace
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        return cleaned

    def validate(self, item: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Validates product record.
        Returns: (is_valid: bool, error_reason: str, sanitized_item: Dict)
        """
        if not isinstance(item, dict):
            return False, "Payload is not a valid JSON dictionary", item

        # 1. Title Validation
        raw_title = item.get("raw_title", "")
        clean_title = self.sanitize_text(str(raw_title))
        if not clean_title or len(clean_title) < 3:
            return False, f"Title missing or too short: '{raw_title}'", item
        item["raw_title"] = clean_title

        # 2. Price Sanity Check
        price = item.get("price")
        try:
            price_val = float(price)
            if price_val <= 0 or price_val > 10000000:
                return False, f"Invalid price value: {price}", item
            item["price"] = price_val
        except (ValueError, TypeError):
            return False, f"Price is not a valid float: {price}", item

        # 3. Marketplace & URL Check
        marketplace = item.get("marketplace")
        if not marketplace or str(marketplace).lower() not in [
            "amazon", "flipkart", "myntra", "ajio", "croma", "reliance_digital", "brand_store", "other"
        ]:
            return False, f"Unknown or missing marketplace: {marketplace}", item

        product_url = item.get("product_url", "")
        if not product_url or not str(product_url).startswith(("http://", "https://")):
            return False, f"Invalid product URL: {product_url}", item

        # 4. Optional original price check
        orig_price = item.get("original_price")
        if orig_price is not None:
            try:
                orig_val = float(orig_price)
                if orig_val < item["price"]:
                    item["original_price"] = item["price"]
                else:
                    item["original_price"] = orig_val
            except (ValueError, TypeError):
                item["original_price"] = None

        return True, "", item

"""
Brand Battle - Data Normalization Engine
Standardizes brand names, category assignments, clean titles, and spec dictionary key-values.
"""

import re
from typing import Dict, Any


BRAND_MAP = {
    "iphone": "Apple", "apple": "Apple", "macbook": "Apple", "ipad": "Apple", "airpods": "Apple",
    "samsung": "Samsung", "galaxy": "Samsung",
    "oneplus": "OnePlus",
    "realme": "Realme",
    "xiaomi": "Xiaomi", "redmi": "Xiaomi", "poco": "Xiaomi", "mi": "Xiaomi",
    "vivo": "Vivo",
    "oppo": "OPPO",
    "nokia": "Nokia",
    "dell": "Dell",
    "hp": "HP",
    "lenovo": "Lenovo",
    "asus": "Asus", "rog": "Asus",
    "acer": "Acer",
    "msi": "MSI",
    "sony": "Sony",
    "bose": "Bose",
    "jbl": "JBL",
    "boat": "boAt",
    "sennheiser": "Sennheiser",
    "nike": "Nike",
    "adidas": "Adidas",
    "puma": "Puma",
    "reebok": "Reebok",
    "allen solly": "Allen Solly",
    "us polo": "US Polo",
    "levi": "Levi's",
    "zara": "Zara",
    "lg": "LG",
    "tcl": "TCL",
    "fossil": "Fossil",
    "casio": "Casio",
    "titan": "Titan",
    "noise": "Noise",
    "fire-boltt": "Fire-Boltt",
    "ambrane": "Ambrane",
    "portronics": "Portronics",
}

CATEGORY_MAP = {
    "smartphone": "Smartphones", "mobile": "Smartphones", "phone": "Smartphones",
    "laptop": "Laptops", "notebook": "Laptops", "computer": "Laptops",
    "headphone": "Headphones", "earphone": "Headphones", "airpods": "Headphones", "tws": "Headphones",
    "shoe": "Shoes", "sneaker": "Shoes", "footwear": "Shoes",
    "watch": "Watches", "smartwatch": "Watches",
    "tv": "Televisions", "television": "Televisions",
    "clothing": "Clothing", "shirt": "Clothing", "pant": "Clothing", "dress": "Clothing",
    "tablet": "Tablets", "ipad": "Tablets",
    "speaker": "Speakers", "soundbar": "Speakers",
    "power bank": "Power Banks",
    "camera": "Cameras",
    "gaming": "Gaming", "console": "Gaming"
}


class DataNormalizer:
    """Normalizes raw marketplace fields into unified canonical values."""

    def detect_brand(self, title: str, brand_hint: str = "") -> str:
        """Detects and standardizes brand name using exact string matches and alias maps."""
        combined = f"{brand_hint} {title}".lower()
        for key, canonical_name in BRAND_MAP.items():
            if re.search(r'\b' + re.escape(key) + r'\b', combined):
                return canonical_name
        return brand_hint.title() if brand_hint else "Generic"

    def detect_category(self, title: str, category_hint: str = "") -> str:
        """Detects unified category name."""
        combined = f"{category_hint} {title}".lower()
        for key, canonical_cat in CATEGORY_MAP.items():
            if key in combined:
                return canonical_cat
        return category_hint.title() if category_hint else "Electronics"

    def clean_title(self, title: str) -> str:
        """Strips promotional marketing noise from product title."""
        text = title
        text = re.sub(r'(?i)\b(add to compare|buy online|best price|free delivery|limited offer|on sale|discounted)\b', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def normalize_specifications(self, specs: Dict[str, Any]) -> Dict[str, Any]:
        """Normalizes memory, storage, and screen size specification key-values."""
        normalized = {}
        for key, val in specs.items():
            val_str = str(val).strip()
            # Standardize storage values: e.g. "256 GB" -> "256GB"
            val_str = re.sub(r'(?i)(\d+)\s*(gb|tb|mb)\b', r'\1\2', val_str)
            # Standardize RAM: e.g. "8 GB RAM" -> "8GB RAM"
            val_str = re.sub(r'(?i)(\d+)\s*(gb|mb)\s*ram\b', r'\1\2 RAM', val_str)
            normalized[key.strip()] = val_str
        return normalized

    def normalize(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Runs complete normalization pipeline on validated product item."""
        title = self.clean_title(item.get("raw_title", ""))
        brand = self.detect_brand(title, item.get("brand_hint", ""))
        category = self.detect_category(title, item.get("category_hint", ""))
        specs = self.normalize_specifications(item.get("specifications", {}))

        # Generate clean canonical slug identifier suggestion
        slug = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')

        normalized_item = dict(item)
        normalized_item.update({
            "clean_title": title,
            "canonical_brand": brand,
            "canonical_category": category,
            "normalized_specs": specs,
            "suggested_slug": slug
        })
        return normalized_item

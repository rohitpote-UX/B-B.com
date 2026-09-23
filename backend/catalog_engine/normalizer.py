"""
Brand Battle — Catalog Normalization Engine
Deterministic normalization for product names, brands, categories,
specifications, and variant attributes.
"""

import re
import unicodedata
from typing import Dict, Any, Optional, Tuple, List


# Canonical Brand Registry & Aliases (dynamically expandable)
BRAND_ALIASES: Dict[str, str] = {
    "apple": "Apple",
    "apple inc": "Apple",
    "apple inc.": "Apple",
    "samsung": "Samsung",
    "samsung electronics": "Samsung",
    "google": "Google",
    "oneplus": "OnePlus",
    "1+": "OnePlus",
    "xiaomi": "Xiaomi",
    "mi": "Xiaomi",
    "redmi": "Redmi",
    "motorola": "Motorola",
    "moto": "Motorola",
    "nothing": "Nothing",
    "realme": "realme",
    "vivo": "vivo",
    "oppo": "OPPO",
    "asus": "ASUS",
    "lenovo": "Lenovo",
    "hp": "HP",
    "hewlett-packard": "HP",
    "dell": "Dell",
    "acer": "Acer",
    "sony": "Sony",
    "boat": "boAt",
    "noise": "Noise",
    "lg": "LG",
}

# Canonical BrandBattle Category Taxonomy
CANONICAL_CATEGORIES: Dict[str, str] = {
    # Mobiles & Tablets
    "mobile": "Mobile Phones",
    "mobiles": "Mobile Phones",
    "mobile phone": "Mobile Phones",
    "smartphone": "Mobile Phones",
    "smartphones": "Mobile Phones",
    "cellphone": "Mobile Phones",
    "handset": "Mobile Phones",
    "tablet": "Tablets",
    "tablets": "Tablets",
    "ipad": "Tablets",

    # Computers & Laptops
    "laptop": "Laptops",
    "laptops": "Laptops",
    "notebook": "Laptops",
    "macbook": "Laptops",
    "pc": "Computers",
    "desktop": "Computers",
    "monitor": "Monitors",
    "monitors": "Monitors",

    # Audio & Wearables
    "headphone": "Headphones",
    "headphones": "Headphones",
    "earphone": "Earbuds",
    "earphones": "Earbuds",
    "earbuds": "Earbuds",
    "tws": "Earbuds",
    "airpods": "Earbuds",
    "smartwatch": "Smartwatches",
    "smartwatches": "Smartwatches",
    "smart watch": "Smartwatches",
    "smart watches": "Smartwatches",
    "wearable": "Smartwatches",
    "fitness band": "Smartwatches",

    # Home & Visual
    "tv": "TVs",
    "tvs": "TVs",
    "television": "TVs",
    "smart tv": "TVs",
    "camera": "Cameras",
    "cameras": "Cameras",
    "dslr": "Cameras",
    "gaming": "Gaming",
    "console": "Gaming",
    "accessories": "Accessories",
}

# Marketing spam phrases to scrub from canonical product titles
TITLE_SPAM_PATTERNS = [
    r"\b(?:online|lowest price|best price|discount|sale|hot deal|best deal|free shipping|fast delivery)\b",
    r"\b(?:with bank offer|exchange offer|no cost emi|cashback)\b",
    r"\b(?:genuine|original|authentic|100% original|brand new)\b",
    r"\b(?:warranty included|1 year warranty|2 year warranty)\b",
    r"\s*\(.*?(?:refurbished|renewed|used).*?\)",
]


class CatalogNormalizer:
    """Provides deterministic string, brand, category, and attribute normalization."""

    @classmethod
    def clean_text(cls, text: Optional[str]) -> str:
        """Normalizes unicode, strips HTML tags, and collapses whitespace."""
        if not text:
            return ""
        # Unicode normalization NFKC
        normalized = unicodedata.normalize("NFKC", str(text))
        # Remove HTML tags
        no_html = re.sub(r"<[^>]+>", " ", normalized)
        # Collapse multiple spaces and newlines
        collapsed = re.sub(r"\s+", " ", no_html).strip()
        return collapsed

    @classmethod
    def clean_title(cls, raw_title: str, brand: Optional[str] = None) -> str:
        """
        Removes promotional spam while preserving model numbers, colors, and variant tags.
        """
        cleaned = cls.clean_text(raw_title)
        for pattern in TITLE_SPAM_PATTERNS:
            cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE)

        # Collapse whitespace after cleaning
        cleaned = re.sub(r"\s+", " ", cleaned).strip()

        # Ensure canonical brand prefix if missing and brand is known
        if brand and not cleaned.lower().startswith(brand.lower()):
            # If title starts with a lowercase or different casing of brand, canonicalize it
            pass

        return cleaned

    @classmethod
    def normalize_brand(cls, raw_brand: Optional[str], title_hint: Optional[str] = None) -> Tuple[str, str]:
        """
        Resolves brand to canonical name.
        Returns: (raw_brand: str, canonical_brand: str)
        """
        raw = cls.clean_text(raw_brand) if raw_brand else ""
        if not raw and title_hint:
            # Attempt to extract brand from title prefix
            first_word = title_hint.strip().split(" ")[0].lower()
            if first_word in BRAND_ALIASES:
                raw = first_word

        lookup = raw.lower().strip()
        canonical = BRAND_ALIASES.get(lookup, raw.title() if raw else "Generic")
        return raw, canonical

    @classmethod
    def normalize_category(cls, raw_category: Optional[str], title_hint: Optional[str] = None) -> Tuple[str, str]:
        """
        Maps raw category to canonical BrandBattle taxonomy.
        Returns: (raw_category: str, canonical_category: str)
        """
        raw = cls.clean_text(raw_category) if raw_category else ""
        text_to_check = (raw + " " + (title_hint or "")).lower()

        canonical = "Electronics"  # safe top-level default
        for key, cat in CANONICAL_CATEGORIES.items():
            pattern = r"\b" + re.escape(key) + r"\b"
            if re.search(pattern, text_to_check):
                canonical = cat
                break

        return raw, canonical

    @classmethod
    def extract_variant_attributes(cls, text: str) -> Dict[str, Any]:
        """
        Extracts structured variant parameters (storage, RAM, color, etc.) from title/specs.
        """
        attrs: Dict[str, Any] = {}
        cleaned = cls.clean_text(text)

        # Storage (e.g., 128GB, 256 GB, 1TB)
        storage_match = re.search(r"\b(16|32|64|128|256|512)\s*(?:GB|gb)\b|\b(1|2)\s*(?:TB|tb)\b", cleaned)
        if storage_match:
            attrs["storage"] = storage_match.group(0).upper().replace(" ", "")

        # RAM (e.g., 8GB RAM, 16 GB RAM)
        ram_match = re.search(r"\b(4|6|8|12|16|18|24|32|64)\s*(?:GB|gb)\s*(?:RAM|ram)\b", cleaned)
        if ram_match:
            attrs["ram"] = ram_match.group(0).upper().replace(" ", "")

        # Common Color Families
        colors = [
            "Natural Titanium", "Desert Titanium", "Black Titanium", "White Titanium",
            "Midnight", "Starlight", "Space Gray", "Space Black", "Silver", "Gold",
            "Rose Gold", "Titanium Gray", "Phantom Black", "Phantom Silver",
            "Deep Purple", "Alpine Green", "Sierra Blue", "Pacific Blue",
            "Black", "White", "Blue", "Green", "Red", "Yellow", "Purple"
        ]
        for color in colors:
            pattern = r"\b" + re.escape(color) + r"\b"
            if re.search(pattern, cleaned, re.IGNORECASE):
                attrs["color"] = color
                break

        return attrs

    @classmethod
    def clean_specifications(cls, raw_specs: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitizes technical specifications dictionary."""
        if not isinstance(raw_specs, dict):
            return {}
        cleaned: Dict[str, Any] = {}
        for k, v in raw_specs.items():
            if not k or not v:
                continue
            clean_k = cls.clean_text(str(k)).title()
            clean_v = cls.clean_text(str(v))
            if clean_k and clean_v:
                cleaned[clean_k] = clean_v
        return cleaned

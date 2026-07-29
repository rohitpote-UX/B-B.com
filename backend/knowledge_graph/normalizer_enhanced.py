"""
Brand Battle - Enhanced Normalizer for Knowledge Graph
Extends the pipeline normalizer with color family, material, gender, subcategory,
product type extraction, and model series/name parsing.
"""

import re
from typing import Dict, Any, Optional, Tuple


# ─── Color Family Normalization ──────────────────────────────────────

COLOR_FAMILY_MAP = {
    # Reds
    "red": "red", "crimson": "red", "scarlet": "red", "maroon": "red",
    "burgundy": "red", "cherry": "red", "ruby": "red", "wine": "red",
    "coral": "red", "rust": "red",
    # Blues
    "blue": "blue", "navy": "blue", "navy blue": "blue", "cobalt": "blue",
    "royal blue": "blue", "sky blue": "blue", "teal": "blue", "turquoise": "blue",
    "cyan": "blue", "indigo": "blue", "sapphire": "blue", "aqua": "blue",
    "ultramarine": "blue",
    # Greens
    "green": "green", "olive": "green", "olive green": "green", "mint": "green",
    "emerald": "green", "sage": "green", "lime": "green", "forest green": "green",
    "khaki": "green", "army green": "green",
    # Blacks / Grays
    "black": "black", "charcoal": "gray", "charcoal gray": "gray",
    "gray": "gray", "grey": "gray", "silver": "gray", "slate": "gray",
    "graphite": "gray", "gunmetal": "gray", "titanium": "gray",
    # Whites / Creams
    "white": "white", "ivory": "white", "cream": "white", "off-white": "white",
    "pearl": "white", "snow": "white", "bone": "white",
    # Yellows / Golds
    "yellow": "yellow", "gold": "gold", "mustard": "yellow",
    "amber": "yellow", "champagne": "gold", "rose gold": "gold",
    # Browns / Tans
    "brown": "brown", "tan": "brown", "beige": "beige", "camel": "brown",
    "chocolate": "brown", "coffee": "brown", "mocha": "brown",
    "taupe": "brown", "sand": "beige", "nude": "beige",
    # Pinks / Purples
    "pink": "pink", "blush": "pink", "rose": "pink", "fuchsia": "pink",
    "magenta": "pink", "salmon": "pink",
    "purple": "purple", "lavender": "purple", "violet": "purple",
    "plum": "purple", "mauve": "purple", "lilac": "purple",
    # Oranges
    "orange": "orange", "peach": "orange", "tangerine": "orange",
    "apricot": "orange", "copper": "orange",
    # Multi / Other
    "multicolor": "multicolor", "multi": "multicolor", "rainbow": "multicolor",
    "camo": "multicolor", "camouflage": "multicolor",
}


# ─── Material Normalization ──────────────────────────────────────────

MATERIAL_MAP = {
    "leather": "leather", "genuine leather": "leather", "faux leather": "faux_leather",
    "synthetic leather": "faux_leather", "pu leather": "faux_leather",
    "cotton": "cotton", "100% cotton": "cotton", "premium cotton": "cotton",
    "pique cotton": "cotton", "oxford cotton": "cotton",
    "polyester": "polyester", "nylon": "nylon", "rayon": "rayon",
    "silk": "silk", "satin": "satin",
    "denim": "denim", "jeans": "denim",
    "wool": "wool", "cashmere": "cashmere", "fleece": "fleece",
    "linen": "linen", "canvas": "canvas",
    "mesh": "mesh", "knit": "knit", "primeknit": "knit",
    "rubber": "rubber", "suede": "suede",
    "metal": "metal", "stainless steel": "stainless_steel", "titanium": "titanium",
    "aluminum": "aluminum", "aluminium": "aluminum",
    "plastic": "plastic", "polycarbonate": "polycarbonate",
    "glass": "glass", "ceramic": "ceramic",
    "carbon fiber": "carbon_fiber", "kevlar": "kevlar",
}


# ─── Gender Detection ────────────────────────────────────────────────

GENDER_KEYWORDS = {
    "men": "men", "mens": "men", "men's": "men", "male": "men",
    "man": "men", "gents": "men", "boys": "men", "boy": "men",
    "women": "women", "womens": "women", "women's": "women", "female": "women",
    "woman": "women", "ladies": "women", "girls": "women", "girl": "women",
    "unisex": "unisex", "gender neutral": "unisex",
    "kids": "kids", "children": "kids", "child": "kids", "junior": "kids",
    "infant": "kids", "toddler": "kids", "baby": "kids",
}


# ─── Product Type Extraction ────────────────────────────────────────

PRODUCT_TYPE_MAP = {
    # Footwear
    "sneaker": "sneakers", "sneakers": "sneakers", "running shoe": "running_shoes",
    "running shoes": "running_shoes", "casual shoe": "casual_shoes",
    "casual shoes": "casual_shoes", "trainer": "sneakers", "trainers": "sneakers",
    "boots": "boots", "boot": "boots", "sandal": "sandals", "sandals": "sandals",
    "slipper": "slippers", "slippers": "slippers", "loafer": "loafers",
    "heel": "heels", "heels": "heels", "flat": "flats",
    # Clothing
    "t-shirt": "tshirt", "tshirt": "tshirt", "tee": "tshirt",
    "shirt": "shirt", "polo": "polo_shirt", "polo shirt": "polo_shirt",
    "jeans": "jeans", "trousers": "trousers", "pants": "trousers",
    "jacket": "jacket", "coat": "coat", "hoodie": "hoodie",
    "sweatshirt": "sweatshirt", "sweater": "sweater",
    "dress": "dress", "skirt": "skirt", "blouse": "blouse",
    "suit": "suit", "blazer": "blazer",
    # Electronics
    "smartphone": "smartphone", "phone": "smartphone", "mobile": "smartphone",
    "laptop": "laptop", "notebook": "laptop",
    "headphone": "headphones", "headphones": "headphones", "earphone": "earphones",
    "earbuds": "earbuds", "earbud": "earbuds", "tws": "earbuds",
    "smartwatch": "smartwatch", "watch": "watch",
    "tablet": "tablet", "television": "television", "tv": "television",
    "camera": "camera", "speaker": "speaker", "soundbar": "soundbar",
    # Accessories
    "bag": "bag", "backpack": "backpack", "wallet": "wallet",
    "belt": "belt", "sunglasses": "sunglasses", "scarf": "scarf",
}


# ─── Subcategory Resolution ─────────────────────────────────────────

SUBCATEGORY_MAP = {
    # Shoes subcategories
    "sneakers": ("Shoes", "Sneakers"), "running_shoes": ("Shoes", "Running Shoes"),
    "casual_shoes": ("Shoes", "Casual Shoes"), "boots": ("Shoes", "Boots"),
    "sandals": ("Shoes", "Sandals"), "slippers": ("Shoes", "Slippers"),
    "loafers": ("Shoes", "Loafers"), "heels": ("Shoes", "Heels"),
    "flats": ("Shoes", "Flats"),
    # Clothing subcategories
    "tshirt": ("Clothing", "T-Shirts"), "shirt": ("Clothing", "Shirts"),
    "polo_shirt": ("Clothing", "Polo Shirts"), "jeans": ("Clothing", "Jeans"),
    "trousers": ("Clothing", "Trousers"), "jacket": ("Clothing", "Jackets"),
    "coat": ("Clothing", "Coats"), "hoodie": ("Clothing", "Hoodies"),
    "sweatshirt": ("Clothing", "Sweatshirts"), "sweater": ("Clothing", "Sweaters"),
    "dress": ("Clothing", "Dresses"), "skirt": ("Clothing", "Skirts"),
    "blouse": ("Clothing", "Blouses"), "suit": ("Clothing", "Suits"),
    "blazer": ("Clothing", "Blazers"),
    # Electronics subcategories
    "smartphone": ("Smartphones", "Smartphones"), "laptop": ("Laptops", "Laptops"),
    "headphones": ("Headphones", "Over-Ear Headphones"),
    "earphones": ("Headphones", "In-Ear Headphones"),
    "earbuds": ("Headphones", "True Wireless Earbuds"),
    "smartwatch": ("Watches", "Smartwatches"), "watch": ("Watches", "Watches"),
    "tablet": ("Tablets", "Tablets"), "television": ("Televisions", "Televisions"),
    "camera": ("Cameras", "Cameras"), "speaker": ("Speakers", "Speakers"),
    "soundbar": ("Speakers", "Soundbars"),
}


# ─── Model Series Patterns ──────────────────────────────────────────

MODEL_SERIES_PATTERNS = [
    # Apple
    (r"(?i)\b(iphone)\s*(\d+)\b", "iPhone", r"\1 \2"),
    (r"(?i)\b(macbook)\s*(pro|air)\b", "MacBook", r"\1 \2"),
    (r"(?i)\b(ipad)\s*(pro|air|mini)?\b", "iPad", r"\1 \2"),
    (r"(?i)\b(airpods)\s*(pro|max)?\b", "AirPods", r"\1 \2"),
    (r"(?i)\b(apple\s*watch)\s*(ultra|se)?\b", "Apple Watch", r"\1 \2"),
    # Samsung
    (r"(?i)\b(galaxy)\s*(s\d+|z\s*fold|z\s*flip|a\d+|m\d+)\s*(ultra|plus|\+|fe)?\b", "Galaxy", None),
    (r"(?i)\b(galaxy)\s*(watch)\s*(\d+)?\s*(ultra|classic)?\b", "Galaxy Watch", None),
    (r"(?i)\b(galaxy)\s*(tab)\s*(s\d+|a\d+)\s*(ultra|plus|\+|fe)?\b", "Galaxy Tab", None),
    # Nike
    (r"(?i)\b(air\s*max)\s*(\d+)?\b", "Air Max", None),
    (r"(?i)\b(air\s*force)\s*(\d+)?\b", "Air Force", None),
    (r"(?i)\b(air\s*jordan)\s*(\d+)?\b", "Air Jordan", None),
    (r"(?i)\b(dunk)\s*(low|high|mid)?\b", "Dunk", None),
    (r"(?i)\b(blazer)\s*(mid|low|high)?\b", "Blazer", None),
    (r"(?i)\b(pegasus)\s*(\d+)?\b", "Pegasus", None),
    (r"(?i)\b(vaporfly)\b", "Vaporfly", None),
    (r"(?i)\b(metcon)\s*(\d+)?\b", "Metcon", None),
    # Adidas
    (r"(?i)\b(ultraboost)\s*(light|\d+)?\b", "Ultraboost", None),
    (r"(?i)\b(samba)\b", "Samba", None),
    (r"(?i)\b(gazelle)\b", "Gazelle", None),
    (r"(?i)\b(superstar)\b", "Superstar", None),
    (r"(?i)\b(nmd)\b", "NMD", None),
    (r"(?i)\b(forum)\b", "Forum", None),
    (r"(?i)\b(campus)\b", "Campus", None),
    # Sony
    (r"(?i)\b(wh-?\d+xm\d+)\b", "WH-1000XM", None),
    (r"(?i)\b(wf-?\d+xm\d+)\b", "WF-1000XM", None),
    # Bose
    (r"(?i)\b(quietcomfort)\s*(ultra|ii|45|35)?\b", "QuietComfort", None),
    # Generic
    (r"(?i)\b(g-?shock)\b", "G-Shock", None),
    (r"(?i)\b(edifice)\b", "Edifice", None),
]


class EnhancedNormalizer:
    """Extended normalizer that extracts rich product identity signals for the Knowledge Graph."""

    def detect_color_family(self, text: str) -> Optional[str]:
        """Detects and normalizes color to a family name."""
        text_lower = text.lower()
        # Check multi-word colors first (e.g., "navy blue" before "blue")
        for color_key in sorted(COLOR_FAMILY_MAP.keys(), key=len, reverse=True):
            if color_key in text_lower:
                return COLOR_FAMILY_MAP[color_key]
        return None

    def detect_material(self, text: str, specs: Dict[str, Any] = None) -> Optional[str]:
        """Detects and normalizes material from title and specifications."""
        combined = text.lower()
        if specs:
            for key, val in specs.items():
                if any(k in key.lower() for k in ["material", "upper", "fabric", "composition"]):
                    combined += " " + str(val).lower()

        for mat_key in sorted(MATERIAL_MAP.keys(), key=len, reverse=True):
            if mat_key in combined:
                return MATERIAL_MAP[mat_key]
        return None

    def detect_gender(self, text: str, specs: Dict[str, Any] = None) -> Optional[str]:
        """Detects gender from title and specifications."""
        combined = text.lower()
        if specs:
            for key, val in specs.items():
                if any(k in key.lower() for k in ["gender", "ideal for", "for"]):
                    combined += " " + str(val).lower()

        for keyword in sorted(GENDER_KEYWORDS.keys(), key=len, reverse=True):
            pattern = r'\b' + re.escape(keyword) + r'\b'
            if re.search(pattern, combined):
                return GENDER_KEYWORDS[keyword]
        return None

    def detect_product_type(self, text: str, category_hint: str = "") -> Optional[str]:
        """Detects normalized product type."""
        combined = f"{category_hint} {text}".lower()
        for type_key in sorted(PRODUCT_TYPE_MAP.keys(), key=len, reverse=True):
            if type_key in combined:
                return PRODUCT_TYPE_MAP[type_key]
        return None

    def resolve_subcategory(self, product_type: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
        """Resolves parent category and subcategory from product type."""
        if product_type and product_type in SUBCATEGORY_MAP:
            return SUBCATEGORY_MAP[product_type]
        return None, None

    def extract_model_series(self, text: str) -> Tuple[Optional[str], Optional[str]]:
        """Extracts model series and full model name from title."""
        for pattern, series_name, _ in MODEL_SERIES_PATTERNS:
            match = re.search(pattern, text)
            if match:
                full_model = match.group(0).strip()
                return series_name, full_model
        return None, None

    def extract_variant(self, text: str, specs: Dict[str, Any] = None) -> Optional[str]:
        """Extracts variant info (storage, size, color combination) from title."""
        parts = []

        # Storage/capacity
        storage_match = re.findall(r'(?i)\b(\d+\s*(?:GB|TB|MB))\b', text)
        if storage_match:
            parts.append(storage_match[0].upper().replace(" ", ""))
        elif specs:
            for key in ["Storage", "Capacity", "Internal Storage"]:
                if key in specs:
                    parts.append(str(specs[key]).strip())
                    break

        # Color from title
        color = self.detect_color_family(text)
        if color:
            parts.append(color.capitalize())

        return " ".join(parts) if parts else None

    def enhance_normalized_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """
        Adds KG-specific normalized fields to an already pipeline-normalized item.
        This is additive — does not remove any existing fields.
        """
        title = item.get("clean_title", item.get("raw_title", ""))
        specs = item.get("normalized_specs", item.get("specifications", {}))
        category_hint = item.get("canonical_category", item.get("category_hint", ""))

        # Color family
        color_family = self.detect_color_family(title)
        if not color_family and specs:
            color_val = specs.get("Color", specs.get("color", ""))
            if color_val:
                color_family = self.detect_color_family(str(color_val))

        # Material
        material = self.detect_material(title, specs)

        # Gender
        gender = self.detect_gender(title, specs)

        # Product type
        product_type = self.detect_product_type(title, category_hint)

        # Subcategory
        parent_cat, subcategory = self.resolve_subcategory(product_type)

        # Model series / model name
        model_series, model_name = self.extract_model_series(title)

        # Variant
        variant = self.extract_variant(title, specs)

        # Enrich the item
        item["kg_color_family"] = color_family
        item["kg_material"] = material
        item["kg_gender"] = gender
        item["kg_product_type"] = product_type
        item["kg_subcategory"] = subcategory
        item["kg_parent_category"] = parent_cat or category_hint
        item["kg_model_series"] = model_series
        item["kg_model_name"] = model_name
        item["kg_variant"] = variant

        return item

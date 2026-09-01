"""
Brand Battle — Category Resolver
Resolves canonical Category IDs, Subcategory IDs, and Family IDs for candidate filtering.
"""

from typing import Dict, Any, Optional, Tuple


# Enterprise Canonical Category Mapping Table
CANONICAL_TAXONOMY_MAP = {
    # Audio
    "headphones": ("CAT_AUDIO", "SUB_HEADPHONES", "FAM_WIRELESS_ANC"),
    "headphone": ("CAT_AUDIO", "SUB_HEADPHONES", "FAM_WIRELESS_ANC"),
    "earbuds": ("CAT_AUDIO", "SUB_EARBUDS", "FAM_TWS"),
    "audio": ("CAT_AUDIO", "SUB_HEADPHONES", "FAM_WIRELESS_ANC"),
    
    # Smartphones
    "smartphones": ("CAT_MOBILE", "SUB_SMARTPHONES", "FAM_FLAGSHIP_PHONE"),
    "smartphone": ("CAT_MOBILE", "SUB_SMARTPHONES", "FAM_FLAGSHIP_PHONE"),
    "mobile": ("CAT_MOBILE", "SUB_SMARTPHONES", "FAM_FLAGSHIP_PHONE"),
    "phones": ("CAT_MOBILE", "SUB_SMARTPHONES", "FAM_FLAGSHIP_PHONE"),
    
    # Laptops
    "laptops": ("CAT_COMPUTING", "SUB_LAPTOPS", "FAM_WORKSTATION_LAPTOP"),
    "laptop": ("CAT_COMPUTING", "SUB_LAPTOPS", "FAM_WORKSTATION_LAPTOP"),
    "computers": ("CAT_COMPUTING", "SUB_LAPTOPS", "FAM_WORKSTATION_LAPTOP"),
    
    # Footwear
    "sneakers": ("CAT_FASHION", "SUB_FOOTWEAR", "FAM_RUNNING_SHOES"),
    "shoes": ("CAT_FASHION", "SUB_FOOTWEAR", "FAM_RUNNING_SHOES"),
}


class CategoryResolver:
    """Resolves canonical IDs (Category, Subcategory, Family) for any product."""

    def resolve_product_taxonomy(self, product: Any) -> Tuple[str, str, str]:
        """
        Returns (category_id, subcategory_id, family_id).
        """
        cat_name = ""
        if hasattr(product, "category") and product.category:
            cat_name = getattr(product.category, "name", str(product.category)).lower()
        elif isinstance(product, dict):
            cat_name = str(product.get("category", "")).lower()

        prod_name = ""
        if hasattr(product, "name"):
            prod_name = str(product.name).lower()
        elif isinstance(product, dict):
            prod_name = str(product.get("name", "")).lower()

        # Check keyword matches in name & category
        combined_text = f"{cat_name} {prod_name}"

        for key, (cat_id, sub_id, fam_id) in CANONICAL_TAXONOMY_MAP.items():
            if key in combined_text:
                return (cat_id, sub_id, fam_id)

        # Fallback to category ID or name hash
        cat_id_num = getattr(product, "category_id", 1) or 1
        return (f"CAT_{cat_id_num}", f"SUB_{cat_id_num}", f"FAM_{cat_id_num}")


category_resolver = CategoryResolver()

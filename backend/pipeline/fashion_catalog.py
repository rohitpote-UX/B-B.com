"""
Brand Battle - Global Fashion Catalogue Generator & AI Style Taxonomy
Generates fashion products across Men's, Women's, Kids, Footwear, Ethnic, Western, Accessories, Watches, Sportswear, and Luxury Fashion.
"""

from typing import List, Dict, Any
import random

IMAGE_PRESETS = {
    "Men Shoes": [
        "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=800",
        "https://images.unsplash.com/photo-1608231387042-66d1773070a5?w=800",
        "https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?w=800",
    ],
    "Women Shoes": [
        "https://images.unsplash.com/photo-1543163521-1bf539c55dd2?w=800",
        "https://images.unsplash.com/photo-1560343090-f0409e92791a?w=800",
    ],
    "Men Clothing": [
        "https://images.unsplash.com/photo-1521572267360-ee0c2909d518?w=800",
        "https://images.unsplash.com/photo-1618354691373-d851c5c3a990?w=800",
    ],
    "Women Clothing": [
        "https://images.unsplash.com/photo-1539109136881-3be0616acf4b?w=800",
        "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?w=800",
    ],
    "Watches": [
        "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=800",
        "https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?w=800",
    ],
    "Bags": [
        "https://images.unsplash.com/photo-1548036328-c9fa89d128fa?w=800",
        "https://images.unsplash.com/photo-1584917865442-de89df76afd3?w=800",
    ]
}

FASHION_STYLE_RECOMMENDATIONS = [
    "Similar Style",
    "Trending Style",
    "Luxury Alternative",
    "Budget Alternative",
    "Seasonal Recommendation",
    "Office Wear",
    "Party Wear",
    "Travel Wear",
    "Street Fashion",
    "Formal",
    "Casual",
    "Minimalist",
    "Premium",
    "Workwear",
]

BRANDS_CATALOG = {
    "Nike": {"category": "Shoes", "sub": "Men Shoes", "models": [("Air Max 270 React", 11995), ("Pegasus 40 Running", 10495)]},
    "Adidas": {"category": "Shoes", "sub": "Men Shoes", "models": [("Ultraboost Light", 15999), ("Samba OG Classic", 9999)]},
    "Levi's": {"category": "Clothing", "sub": "Men Clothing", "models": [("501 Original Fit Jeans", 3999), ("Trucker Denim Jacket", 5999)]},
    "Zara": {"category": "Clothing", "sub": "Women Clothing", "models": [("Floral Print Wrap Dress", 3590), ("Wool Coat", 8990)]},
    "Fossil": {"category": "Watches", "sub": "Watches", "models": [("Nate Chronograph Watch", 13495)]},
}


def generate_fashion_catalog(count: int = 100) -> List[Dict[str, Any]]:
    """Generates structured fashion items with 18 explicit attributes."""
    items: List[Dict[str, Any]] = []
    marketplaces = ["amazon", "flipkart", "myntra", "ajio"]
    brand_names = list(BRANDS_CATALOG.keys())

    for i in range(count):
        brand = brand_names[i % len(brand_names)]
        info = BRANDS_CATALOG[brand]
        model_name, base_price = info["models"][i % len(info["models"])]
        mp = marketplaces[i % len(marketplaces)]

        item = {
            "raw_title": f"{brand} {model_name} Edition #{i + 1}",
            "marketplace": mp,
            "price": float(base_price),
            "original_price": round(base_price * 1.25, -1),
            "currency": "INR",
            "product_url": f"https://www.{mp}.com/product/{brand.lower()}-{i}",
            "image_url": IMAGE_PRESETS.get(info["sub"], IMAGE_PRESETS["Men Clothing"])[0],
            "brand_hint": brand,
            "category_hint": info["category"],
            "specifications": {
                "Brand": brand,
                "Material": "100% Premium Cotton" if info["category"] == "Clothing" else "Genuine Leather & Mesh",
                "Fabric": "Denim / Cotton Twill" if info["category"] == "Clothing" else "Synthetic Mesh",
                "Fit": "Regular Fit",
                "Pattern": "Solid Classic",
                "Sleeve Type": "Full Sleeve" if info["category"] == "Clothing" else "N/A",
                "Collar": "Spread Collar" if info["category"] == "Clothing" else "N/A",
                "Length": "Regular Length",
                "Closure": "Button / Zipper",
                "Occasion": "Casual / Party Wear",
                "Season": "All Season 2026",
                "Style": "Modern Minimalist",
                "Color Family": "Black / Navy",
                "Size": "M / L / XL",
                "Gender": "Women" if "Women" in info["sub"] else "Men",
                "Collection": "2026 Global Flagship",
                "Care Instructions": "Machine Wash Warm",
                "Country of Origin": "India",
            },
            "rating": 4.5,
            "total_reviews": 320,
            "seller_name": f"{brand} Official Flagship",
            "availability": True,
        }
        items.append(item)

    return items

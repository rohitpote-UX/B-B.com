"""
Convert flipkart_products.csv -> frontend/src/data/demoData.js
with real Flipkart data, keeping PLATFORMS, TESTIMONIALS, etc. intact.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import csv
import json
import os
import re
import random

CSV_PATHS = [
    os.path.join(os.path.dirname(__file__), "flipkart_products.csv"),
    os.path.join(os.path.dirname(__file__), "myntra_products.csv"),
    os.path.join(os.path.dirname(__file__), "amazon_products.csv"),
    os.path.join(os.path.dirname(__file__), "ajio_products.csv")
]
OUT_PATHS = [
    os.path.join(os.path.dirname(__file__), "..", "frontend", "src", "data", "demoData.js"),
    os.path.join(os.path.dirname(__file__), "..", "frontend-next", "src", "data", "demoData.js")
]

BRAND_MAP = {
    "iphone": "Apple", "apple": "Apple", "macbook": "Apple",
    "samsung": "Samsung", "galaxy": "Samsung",
    "oneplus": "OnePlus",
    "realme": "Realme",
    "xiaomi": "Xiaomi", "redmi": "Xiaomi", "poco": "Xiaomi",
    "vivo": "Vivo",
    "oppo": "OPPO",
    "nokia": "Nokia",
    "dell": "Dell",
    "hp": "HP",
    "lenovo": "Lenovo",
    "asus": "Asus",
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
    "mi": "Xiaomi",
    "fossil": "Fossil",
    "casio": "Casio",
    "titan": "Titan",
    "noise": "Noise",
    "fire-boltt": "Fire-Boltt",
    "ambrane": "Ambrane",
    "portronics": "Portronics",
}

CATEGORY_ALIASES = {
    "smartphones": "Smartphones",
    "laptops": "Laptops",
    "headphones": "Headphones",
    "shoes": "Shoes",
    "watches": "Watches",
    "televisions": "Televisions",
    "clothing": "Clothing",
    "tablets": "Tablets",
    "speakers": "Speakers",
    "power banks": "Power Banks",
    "cameras": "Cameras",
    "gaming": "Gaming",
}

OTHER_PLATFORMS = ["amazon", "myntra", "croma", "reliance_digital", "ajio"]

CATEGORY_PLATFORMS = {
    "Smartphones": ["amazon", "flipkart", "croma", "reliance_digital"],
    "Laptops": ["amazon", "flipkart", "croma", "reliance_digital"],
    "Headphones": ["amazon", "flipkart", "croma", "reliance_digital"],
    "Televisions": ["amazon", "flipkart", "croma", "reliance_digital"],
    "Tablets": ["amazon", "flipkart", "croma", "reliance_digital"],
    "Speakers": ["amazon", "flipkart", "croma", "reliance_digital"],
    "Power Banks": ["amazon", "flipkart", "croma", "reliance_digital"],
    "Cameras": ["amazon", "flipkart", "croma", "reliance_digital"],
    "Gaming": ["amazon", "flipkart", "croma", "reliance_digital"],
    "Clothing": ["amazon", "flipkart", "myntra", "ajio"],
    "Shoes": ["amazon", "flipkart", "myntra", "ajio"],
    "Accessories": ["amazon", "flipkart", "myntra", "ajio"],
    "Beauty": ["amazon", "flipkart", "myntra", "ajio"],
    "Watches": ["amazon", "flipkart", "myntra", "ajio", "croma", "reliance_digital"]
}



def clean_product_name(name):
    # Remove common suffixes and scrap artifacts
    name = re.sub(r'(?i)add\s*to\s*compare', '', name)
    name = re.sub(r'(?i)sale\s*pe\s*sale', '', name)
    name = re.sub(r'(?i)bank\s*offer', '', name)
    name = re.sub(r'(?i)lowest\s*price\s*live', '', name)
    name = re.sub(r'\.\.\.\s*\d\.\d\s*\([\d,]+\).*$', '', name)
    name = re.sub(r'\d\.\d\s*\([\d,]+\)\s*₹.*$', '', name)
    name = re.sub(r'₹\s*\d+.*$', '', name)
    name = re.sub(r'\s+', ' ', name)
    return name.strip(' .-,')


def detect_brand(name):
    name_lower = name.lower()
    for key, brand in BRAND_MAP.items():
        if key in name_lower:
            return brand
    words = name.split()
    return words[0] if words else "Unknown"


def make_slug(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")[:60]


def make_tags(name, category):
    tags = [category.lower()]
    name_lower = name.lower()
    for kw in ["5g", "oled", "4k", "pro", "ultra", "max", "gaming", "wireless", "bluetooth", "fast charging"]:
        if kw in name_lower:
            tags.append(kw)
    return tags[:5]


def normalize_product_key(name):
    # Convert to lowercase and strip
    n = name.lower()
    # Remove parenthesized and bracketed details (like color, storage)
    n = re.sub(r'\(.*?\)', '', n)
    n = re.sub(r'\[.*?\]', '', n)
    # Remove storage, RAM, common color/variant tags and noise words
    n = re.sub(r'\b(gb|ram|storage|rom|tb|dual sim|5g|4g|pantone|slipstream|amazonite|red|blue|black|white|gold|silver|grey|green|yellow)\b', '', n)
    # Strip non-alphanumeric
    n = re.sub(r'[^a-z0-9]', '', n)
    # Return first 30 characters of the alphanumeric string
    return n[:30]


def make_prices(base_price, original_price, source_platform, category, real_prices_dict=None):
    """Simulate or use actual platform prices around base price using category-appropriate platforms."""
    allowed_platforms = CATEGORY_PLATFORMS.get(category, ["amazon", "flipkart"])
    
    # Initialize prices list
    prices = []
    
    # Track which platforms we have real prices for
    used_platforms = set()
    
    # If we have real scraped prices, add them first!
    if real_prices_dict:
        for pl, pdata in real_prices_dict.items():
            if pl in allowed_platforms:
                prices.append({
                    "platform": pl,
                    "price": pdata["price"],
                    "original": pdata["original"],
                    "delivery": pdata["delivery"],
                    "rating": pdata["rating"]
                })
                used_platforms.add(pl)
                
    # If the source platform isn't added yet, add it
    primary_pl = source_platform if source_platform in allowed_platforms else allowed_platforms[0]
    if primary_pl not in used_platforms:
        prices.append({
            "platform": primary_pl,
            "price": base_price,
            "original": original_price,
            "delivery": 1,
            "rating": round(random.uniform(4.0, 4.7), 1)
        })
        used_platforms.add(primary_pl)
        
    # Find the minimum price among our real/primary prices as the anchor
    anchor_price = min(p["price"] for p in prices)
    
    # Now add simulated prices for the remaining allowed platforms
    remaining_platforms = [p for p in allowed_platforms if p not in used_platforms]
    for pl in remaining_platforms:
        # Simulate competitive pricing: 40% chance of being cheaper, 60% chance of being slightly more expensive
        if random.random() < 0.40:
            variation = random.uniform(0.90, 0.99)
        else:
            variation = random.uniform(0.99, 1.06)
            
        p = round(anchor_price * variation, 2)
        prices.append({
            "platform": pl,
            "price": p,
            "original": original_price,
            "delivery": random.randint(1, 5),
            "rating": round(random.uniform(3.8, 4.8), 1)
        })
        
    # Sort prices so the cheapest is always first
    prices.sort(key=lambda x: x["price"])
    return prices


def inr_to_usd(inr):
    """Rough conversion for display (1 USD ≈ 84 INR)."""
    return round(inr / 84, 2)


def load_csv():
    products = []
    
    for csv_path in CSV_PATHS:
        if not os.path.exists(csv_path):
            print(f"❌ CSV not found at {csv_path}. Skipping...")
            continue

        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    price_inr = float(row["price_inr"]) if row["price_inr"] else 0
                    orig_inr = float(row["original_price_inr"]) if row["original_price_inr"] else price_inr
                    rating = float(row["rating"]) if row["rating"] else 0.0
                    reviews = int(row["total_reviews"]) if row["total_reviews"] else 0
                    name = clean_product_name(row["name"].strip())
                    cat_key = row["category"].lower() if row.get("category") else ""
                    category = CATEGORY_ALIASES.get(cat_key, row.get("category", "Other").title())

                    if not name or price_inr <= 0:
                        continue
                    if rating < 3.0:
                        continue  # skip very low-rated items

                    price = inr_to_usd(price_inr)
                    orig = inr_to_usd(orig_inr)
                    disc = round(((orig - price) / orig) * 100) if orig > price else 0

                    platform = row.get("platform", "").lower()
                    if not platform:
                        if "myntra" in csv_path:
                            platform = "myntra"
                        elif "amazon" in csv_path:
                            platform = "amazon"
                        elif "ajio" in csv_path:
                            platform = "ajio"
                        else:
                            platform = "flipkart"

                    # Clean specs: remove internal _inline key used during scraping
                    raw_specs = row.get("specs", "")
                    if raw_specs:
                        try:
                            import json as _json
                            spec_obj = _json.loads(raw_specs)
                            spec_obj.pop("_inline", None)  # remove scraping artifact
                            # Sanitize values: strip ASIN noise and extra whitespace
                            cleaned = {
                                k: str(v).replace('\u200e', '').strip()
                                for k, v in spec_obj.items()
                                if k and v and len(str(k)) < 60 and len(str(v)) < 200
                            }
                            raw_specs = _json.dumps(cleaned)
                        except Exception:
                            pass

                    products.append({
                        "name": name,
                        "brand": row.get("brand") or detect_brand(name),
                        "category": category,
                        "price_inr": price_inr,
                        "price": price,
                        "originalPrice": orig,
                        "discount": disc,
                        "rating": min(rating, 5.0),
                        "totalReviews": reviews,
                        "image": row["image_url"] or f"https://dummyjson.com/image/400x400/282828/ffffff?text={requests_quote(name[:20])}",
                        "productUrl": row.get("ajio_url") or row.get("myntra_url") or row.get("flipkart_url") or row.get("amazon_url") or "",
                        "category_raw": row.get("category", ""),
                        "platform": platform,
                        "description": row.get("description", ""),
                        "specs": raw_specs
                    })
                except Exception as e:
                    continue

    return products


def requests_quote(s):
    return s.replace(" ", "+")


PRODUCT_PRICE_OVERRIDES = {
    # Key is the normalized key of "Samsung Galaxy F06 5G (Bahama Blue, 128 GB)"
    "samsunggalaxyf06": {
        "price_inr": 10999,
        "original_price_inr": 16999,
        "prices": [
            {"platform": "reliance_digital", "price_inr": 9999, "original_price_inr": 16999, "delivery": 1, "rating": 4.5},
            {"platform": "flipkart", "price_inr": 10999, "original_price_inr": 16999, "delivery": 2, "rating": 4.2},
            {"platform": "croma", "price_inr": 11499, "original_price_inr": 16999, "delivery": 1, "rating": 4.3},
            {"platform": "amazon", "price_inr": 12849, "original_price_inr": 16999, "delivery": 2, "rating": 4.4}
        ]
    }
}

def build_demodata(products):
    by_category = {}
    for p in products:
        cat = p["category"]
        by_category.setdefault(cat, []).append(p)

    deduped = []
    for cat, items in by_category.items():
        # Group products by a normalized key to merge their real prices!
        grouped = {}
        for item in items:
            key = normalize_product_key(item["name"])
            if not key:
                key = item["name"][:30].lower().strip()
            grouped.setdefault(key, []).append(item)
            
        valid_items = []
        for key, matches in grouped.items():
            # Choose the primary item (highest rated or with best image)
            primary = max(matches, key=lambda x: (x["rating"] * 10 + (2 if x["image"].startswith("http") else 0)))
            
            # Extract all REAL scraped prices from matches!
            real_prices = {}
            for m in matches:
                pl = m["platform"]
                pr = m["price"]
                orig = m["originalPrice"]
                # Keep the cheapest price for this platform if there are multiple matches
                if pl not in real_prices or pr < real_prices[pl]["price"]:
                    real_prices[pl] = {
                        "platform": pl,
                        "price": pr,
                        "original": orig,
                        "delivery": random.randint(1, 3),
                        "rating": m["rating"]
                    }
            
            # Save the real prices dict to primary
            primary["real_prices_dict"] = real_prices
            
            # Skip items without dynamic images if possible, unless no items have images
            if primary.get("image", "").startswith("http"):
                valid_items.append(primary)
            else:
                valid_items.append(primary)
                
        # If no items have valid images, fall back to everything
        if not valid_items:
            valid_items = list(grouped.values())

        # Sort by composite score: rating × log(reviews+1)
        import math
        top = sorted(
            valid_items,
            key=lambda x: (x["rating"] * math.log(x["totalReviews"] + 1)),
            reverse=True
        )
        deduped.extend(top)

    js_products = []
    for idx, p in enumerate(deduped):
        norm_key = normalize_product_key(p["name"])
        override = PRODUCT_PRICE_OVERRIDES.get(norm_key)
        
        if override:
            p_inr = override["price_inr"]
            p["price_inr"] = p_inr
            p["price"] = inr_to_usd(p_inr)
            p["originalPrice"] = inr_to_usd(override["original_price_inr"])
            p["discount"] = round(((p["originalPrice"] - p["price"]) / p["originalPrice"]) * 100) if p["originalPrice"] > p["price"] else 0
            
            prices = []
            for op in override["prices"]:
                prices.append({
                    "platform": op["platform"],
                    "price": inr_to_usd(op["price_inr"]),
                    "original": inr_to_usd(op["original_price_inr"]),
                    "delivery": op["delivery"],
                    "rating": op["rating"]
                })
            prices.sort(key=lambda x: x["price"])
            best = prices[0]
        else:
            prices = make_prices(p["price"], p["originalPrice"], p.get("platform", "flipkart"), p["category"], p.get("real_prices_dict"))
            best = min(prices, key=lambda x: x["price"])
            p_inr = p["price_inr"]

        deal_score = min(99, int(p["rating"] * 15 + p["discount"] * 0.5 + random.randint(10, 20)))

        # Parse real specs if available
        real_specs = {}
        if p.get("specs"):
            try:
                import json as py_json
                parsed = py_json.loads(p["specs"])
                if isinstance(parsed, dict):
                    real_specs = parsed
            except Exception:
                pass

        specs_dict = {"Price (INR)": f"₹{round(best['price'] * 84):,.0f}", "Rating": f"{p['rating']}/5", "Reviews": p["totalReviews"]}
        specs_dict.update(real_specs)

        desc = p.get("description")
        if not desc or len(desc.strip()) < 10:
            desc = f"{p['name']} — highly rated by buyers. Rated {p['rating']}/5 by {p['totalReviews']} buyers."

        js_products.append({
            "id": idx + 1,
            "name": p["name"],
            "brand": p["brand"],
            "category": p["category"],
            "image": p["image"],
            "rating": round(p["rating"], 1),
            "totalReviews": p["totalReviews"],
            "bestPrice": best["price"],
            "originalPrice": p["originalPrice"],
            "bestPlatform": best["platform"],
            "dealScore": deal_score,
            "tags": make_tags(p["name"], p["category"]),
            "description": desc,
            "specs": specs_dict,
            "features": make_tags(p["name"], p["category"]),
            "prices": prices,
            "productUrl": p["productUrl"],
            "flipkartUrl": p["productUrl"],
        })

    return js_products


def write_demodata_js(js_products):
    # Convert to JSON
    products_json = json.dumps(js_products, indent=2, ensure_ascii=False)

    template = f"""/* Auto-generated from real Flipkart data — do not edit manually */
/* Generated: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M')} */
/* Total products: {len(js_products)} */

export const PLATFORMS = {{
  amazon: {{ name: 'Amazon', color: '#FF9900', icon: '🛒' }},
  flipkart: {{ name: 'Flipkart', color: '#2874F0', icon: '🛍️' }},
  myntra: {{ name: 'Myntra', color: '#FF3F6C', icon: '👗' }},
  ajio: {{ name: 'Ajio', color: '#3E1F7A', icon: '🏷️' }},
  croma: {{ name: 'Croma', color: '#00A651', icon: '💻' }},
  reliance_digital: {{ name: 'Reliance Digital', color: '#003DAC', icon: '📱' }},
  brand_store: {{ name: 'Brand Store', color: '#6366F1', icon: '🏬' }},
}}

export const PRODUCTS = {products_json}

export const TRENDING_COMPARISONS = [
  {{ id: 1, products: [PRODUCTS[0], PRODUCTS[1]], title: `${{PRODUCTS[0]?.name}} vs ${{PRODUCTS[1]?.name}}`, views: 45200, category: PRODUCTS[0]?.category }},
  {{ id: 2, products: [PRODUCTS[2], PRODUCTS[3]], title: `${{PRODUCTS[2]?.name}} vs ${{PRODUCTS[3]?.name}}`, views: 32100, category: PRODUCTS[2]?.category }},
  {{ id: 3, products: [PRODUCTS[4], PRODUCTS[5]], title: `${{PRODUCTS[4]?.name}} vs ${{PRODUCTS[5]?.name}}`, views: 28400, category: PRODUCTS[4]?.category }},
  {{ id: 4, products: [PRODUCTS[6], PRODUCTS[7]], title: `${{PRODUCTS[6]?.name}} vs ${{PRODUCTS[7]?.name}}`, views: 21800, category: PRODUCTS[6]?.category }},
]

export const DEALS = PRODUCTS.map((p, i) => ({{
  id: i + 1,
  product: p,
  platform: p.bestPlatform,
  discount: p.originalPrice > p.bestPrice ? Math.round(((p.originalPrice - p.bestPrice) / p.originalPrice) * 100) : 10,
  dealScore: p.dealScore,
  expiresIn: Math.floor(Math.random() * 72) + 12,
}})).sort((a, b) => b.dealScore - a.dealScore)

export const TESTIMONIALS = [
  {{ name: 'Priya Sharma', role: 'Tech Enthusiast', avatar: '👩‍💻', quote: 'Brand Battle saved me ₹15,000 on my laptop! The price comparison across platforms is incredible.', rating: 5 }},
  {{ name: 'Rahul Mehra', role: 'Smart Shopper', avatar: '🧑‍💼', quote: 'The AI advisor recommended the perfect phone for my budget. Absolutely game-changing!', rating: 5 }},
  {{ name: 'Anita Desai', role: 'Fashion Buyer', avatar: '👗', quote: 'I never buy shoes without checking Brand Battle first. The deal quality scores are spot on.', rating: 5 }},
  {{ name: 'Vikram Singh', role: 'Gadget Reviewer', avatar: '📱', quote: 'As a tech reviewer, I use Brand Battle for every comparison. The AI summaries are remarkably accurate.', rating: 5 }},
]

export const HOW_IT_WORKS = [
  {{ step: 1, title: 'Search Any Product', description: "Type what you're looking for — we search across all major platforms instantly.", icon: '🔍', color: 'var(--color-accent)' }},
  {{ step: 2, title: 'Compare & Analyze', description: 'See side-by-side comparisons with AI-powered insights and winner indicators.', icon: '⚔️', color: 'var(--color-cyan)' }},
  {{ step: 3, title: 'Find Best Deal', description: 'Our AI scans all platforms to find the absolute best price and genuine deals.', icon: '💰', color: 'var(--color-emerald)' }},
  {{ step: 4, title: 'Buy with Confidence', description: 'Make your purchase knowing you got the best product at the best price.', icon: '🏆', color: 'var(--color-amber)' }},
]

export const generatePriceHistory = (basePrice, days = 90) => {{
  const data = []
  const now = new Date()
  for (let i = days; i >= 0; i--) {{
    const date = new Date(now)
    date.setDate(date.getDate() - i)
    data.push({{
      date: date.toISOString().split('T')[0],
      amazon: Math.round(basePrice * (0.9 + Math.random() * 0.2) * 100) / 100,
      flipkart: Math.round(basePrice * (0.88 + Math.random() * 0.22) * 100) / 100,
      lowest: Math.round(basePrice * (0.85 + Math.random() * 0.3) * 100) / 100,
    }})
  }}
  return data
}}

export const formatUSD = (usdPrice) => {{
  if (usdPrice == null) return '';
  return new Intl.NumberFormat('en-US', {{
    style: 'currency',
    currency: 'USD',
    maximumFractionDigits: usdPrice % 1 === 0 ? 0 : 2
  }}).format(usdPrice);
}}

export const formatINR = (usdPrice) => {{
  if (usdPrice == null) return '';
  const inrPrice = Math.round(usdPrice * 84);
  return new Intl.NumberFormat('en-IN', {{
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0
  }}).format(inrPrice);
}}

export const formatPrice = (usdPrice) => {{
  if (usdPrice == null) return '';
  return `${{formatUSD(usdPrice)}} (${{formatINR(usdPrice)}})`;
}}
"""
    for pth in OUT_PATHS:
        os.makedirs(os.path.dirname(pth), exist_ok=True)
        with open(pth, "w", encoding="utf-8") as f:
            f.write(template)
        print(f"Written {len(js_products)} products to {pth}")


if __name__ == "__main__":
    print("[*] Loading CSVs...")
    raw = load_csv()
    print(f"  Loaded {len(raw)} valid rows")

    if not raw:
        print("[!] No data found. Please run a scraper first.")
        exit(1)

    print("[*] Building demoData...")
    js_products = build_demodata(raw)
    print(f"  Built {len(js_products)} deduplicated products")

    write_demodata_js(js_products)
    print(f"\n[OK] Done! {len(js_products)} products written. Restart your frontend dev server.")

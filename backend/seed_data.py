"""
Brand Battle - Seed Data
Populates the database with realistic demo products, brands, prices,
reviews, deals, comparisons, and users for development and demonstration.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from datetime import datetime, timedelta, timezone
import random
import json

from database import engine, SessionLocal, Base
from models import (
    User, Brand, Category, Product, Price, PriceHistory,
    Review, Comparison, Deal, AffiliateLink, Notification
)
from auth import hash_password


def seed_database():
    """Seed the database with demo data."""
    # Create tables
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # Check if already seeded
        if db.query(User).count() > 0:
            print("Database already seeded. Skipping.")
            return

        print("🌱 Seeding database...")

        # ─── Users ───────────────────────────────────────────
        admin = User(
            email="admin@brandbattle.com",
            username="admin",
            hashed_password=hash_password("admin123456"),
            full_name="Admin User",
            role="admin",
            is_active=True,
            is_verified=True,
        )
        demo_user = User(
            email="demo@brandbattle.com",
            username="demo",
            hashed_password=hash_password("demo123456"),
            full_name="Demo User",
            role="user",
            is_active=True,
            is_verified=True,
        )
        db.add_all([admin, demo_user])
        db.flush()
        print("  ✅ Users created")

        # ─── Categories ──────────────────────────────────────
        categories_data = [
            {"name": "Smartphones", "slug": "smartphones", "icon": "smartphone"},
            {"name": "Laptops", "slug": "laptops", "icon": "laptop"},
            {"name": "Shoes", "slug": "shoes", "icon": "footprints"},
            {"name": "Clothing", "slug": "clothing", "icon": "shirt"},
            {"name": "Headphones", "slug": "headphones", "icon": "headphones"},
            {"name": "Watches", "slug": "watches", "icon": "watch"},
            {"name": "Televisions", "slug": "televisions", "icon": "tv"},
            {"name": "Cameras", "slug": "cameras", "icon": "camera"},
            {"name": "Tablets", "slug": "tablets", "icon": "tablet"},
            {"name": "Gaming", "slug": "gaming", "icon": "gamepad-2"},
        ]

        categories = {}
        for cat_data in categories_data:
            cat = Category(**cat_data)
            db.add(cat)
            db.flush()
            categories[cat.slug] = cat
        print("  ✅ Categories created")

        # ─── Brands ──────────────────────────────────────────
        brands_data = [
            {"name": "Apple", "slug": "apple", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/f/fa/Apple_logo_black.svg", "website_url": "https://apple.com", "trust_score": 9.4, "customer_satisfaction": 9.2, "return_rate": 2.1, "review_sentiment": 0.91, "durability_score": 9.0, "category": "Electronics", "is_verified": True},
            {"name": "Samsung", "slug": "samsung", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/2/24/Samsung_Logo.svg", "website_url": "https://samsung.com", "trust_score": 8.8, "customer_satisfaction": 8.5, "return_rate": 3.2, "review_sentiment": 0.85, "durability_score": 8.5, "category": "Electronics", "is_verified": True},
            {"name": "Nike", "slug": "nike", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/a/a6/Logo_NIKE.svg", "website_url": "https://nike.com", "trust_score": 9.2, "customer_satisfaction": 8.9, "return_rate": 4.5, "review_sentiment": 0.88, "durability_score": 8.8, "category": "Fashion", "is_verified": True},
            {"name": "Adidas", "slug": "adidas", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/2/20/Adidas_Logo.svg", "website_url": "https://adidas.com", "trust_score": 8.7, "customer_satisfaction": 8.4, "return_rate": 5.0, "review_sentiment": 0.84, "durability_score": 8.3, "category": "Fashion", "is_verified": True},
            {"name": "Sony", "slug": "sony", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/c/ca/Sony_logo.svg", "website_url": "https://sony.com", "trust_score": 9.0, "customer_satisfaction": 8.7, "return_rate": 2.8, "review_sentiment": 0.87, "durability_score": 9.1, "category": "Electronics", "is_verified": True},
            {"name": "Dell", "slug": "dell", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/1/18/Dell_logo_2016.svg", "website_url": "https://dell.com", "trust_score": 8.3, "customer_satisfaction": 8.0, "return_rate": 4.2, "review_sentiment": 0.79, "durability_score": 8.0, "category": "Electronics", "is_verified": True},
            {"name": "HP", "slug": "hp", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/a/ad/HP_logo_2012.svg", "website_url": "https://hp.com", "trust_score": 8.0, "customer_satisfaction": 7.8, "return_rate": 4.8, "review_sentiment": 0.76, "durability_score": 7.8, "category": "Electronics", "is_verified": True},
            {"name": "Allen Solly", "slug": "allen-solly", "website_url": "https://allensolly.com", "trust_score": 7.8, "customer_satisfaction": 7.5, "return_rate": 6.0, "review_sentiment": 0.74, "durability_score": 7.2, "category": "Fashion", "is_verified": True},
            {"name": "US Polo", "slug": "us-polo", "website_url": "https://uspoloassn.com", "trust_score": 7.5, "customer_satisfaction": 7.3, "return_rate": 6.5, "review_sentiment": 0.72, "durability_score": 7.0, "category": "Fashion", "is_verified": True},
            {"name": "OnePlus", "slug": "oneplus", "website_url": "https://oneplus.com", "trust_score": 8.5, "customer_satisfaction": 8.3, "return_rate": 3.5, "review_sentiment": 0.83, "durability_score": 8.2, "category": "Electronics", "is_verified": True},
            {"name": "Bose", "slug": "bose", "website_url": "https://bose.com", "trust_score": 9.1, "customer_satisfaction": 9.0, "return_rate": 2.5, "review_sentiment": 0.90, "durability_score": 9.2, "category": "Electronics", "is_verified": True},
            {"name": "JBL", "slug": "jbl", "website_url": "https://jbl.com", "trust_score": 8.4, "customer_satisfaction": 8.2, "return_rate": 3.8, "review_sentiment": 0.82, "durability_score": 8.0, "category": "Electronics", "is_verified": True},
        ]

        brands = {}
        for brand_data in brands_data:
            brand = Brand(**brand_data)
            db.add(brand)
            db.flush()
            brands[brand.slug] = brand
        print("  ✅ Brands created")

        # ─── Products ────────────────────────────────────────
        products_data = [
            # Smartphones
            {
                "name": "iPhone 17 Pro Max",
                "slug": "iphone-17-pro-max",
                "brand": "apple",
                "category": "smartphones",
                "description": "The most advanced iPhone ever. Featuring the A19 Pro chip, 48MP quad camera system, titanium design, and all-day battery life.",
                "short_description": "Apple's flagship with A19 Pro chip and 48MP camera",
                "image_url": "https://dummyjson.com/image/400x400/282828/ffffff?text=iPhone+17+Pro",
                "images": ["https://dummyjson.com/image/400x400/282828/ffffff?text=iPhone+17+Front", "https://dummyjson.com/image/400x400/282828/ffffff?text=iPhone+17+Back", "https://dummyjson.com/image/400x400/282828/ffffff?text=iPhone+17+Side"],
                "specifications": {"Display": "6.9-inch Super Retina XDR OLED", "Chip": "A19 Pro", "RAM": 12, "Storage": "256GB", "Battery": 4852, "Camera": "48MP Quad", "OS": "iOS 19", "5G": True, "Weight": "221g"},
                "features": ["A19 Pro Chip", "48MP Camera System", "Titanium Design", "USB-C", "All-day Battery", "ProMotion 120Hz", "Face ID", "Satellite SOS"],
                "tags": ["smartphone", "apple", "iphone", "flagship", "premium"],
                "average_rating": 4.7,
                "total_reviews": 2847,
            },
            {
                "name": "Samsung Galaxy S26 Ultra",
                "slug": "samsung-galaxy-s26-ultra",
                "brand": "samsung",
                "category": "smartphones",
                "description": "Galaxy AI powered experience with 200MP camera, Snapdragon 8 Gen 5, S Pen, and titanium frame.",
                "short_description": "Samsung's AI-powered flagship with 200MP camera",
                "image_url": "https://dummyjson.com/image/400x400/1a1a2e/ffffff?text=Galaxy+S26",
                "images": ["https://dummyjson.com/image/400x400/1a1a2e/ffffff?text=S26+Front", "https://dummyjson.com/image/400x400/1a1a2e/ffffff?text=S26+Back"],
                "specifications": {"Display": "6.8-inch Dynamic AMOLED 2X", "Chip": "Snapdragon 8 Gen 5", "RAM": 16, "Storage": "256GB", "Battery": 5500, "Camera": "200MP Quad", "OS": "Android 16 + One UI 8", "5G": True, "Weight": "228g"},
                "features": ["Galaxy AI", "200MP Camera", "S Pen", "Snapdragon 8 Gen 5", "5000mAh Battery", "IP68 Water Resistant", "120Hz LTPO"],
                "tags": ["smartphone", "samsung", "galaxy", "flagship", "android"],
                "average_rating": 4.6,
                "total_reviews": 3125,
            },
            {
                "name": "OnePlus 14 Pro",
                "slug": "oneplus-14-pro",
                "brand": "oneplus",
                "category": "smartphones",
                "description": "Speed meets style. Hasselblad cameras, 100W fast charging, and flagship Snapdragon performance.",
                "short_description": "OnePlus flagship with Hasselblad cameras",
                "image_url": "https://dummyjson.com/image/400x400/2d1b4e/ffffff?text=OnePlus+14",
                "specifications": {"Display": "6.7-inch LTPO AMOLED", "Chip": "Snapdragon 8 Gen 5", "RAM": 16, "Storage": "256GB", "Battery": 5400, "Camera": "50MP Triple Hasselblad", "OS": "OxygenOS 15", "5G": True},
                "features": ["Hasselblad Camera", "100W SUPERVOOC", "Snapdragon 8 Gen 5", "LTPO AMOLED", "Alert Slider"],
                "tags": ["smartphone", "oneplus", "flagship", "fast-charging"],
                "average_rating": 4.5,
                "total_reviews": 1856,
            },
            # Laptops
            {
                "name": "MacBook Pro 16-inch M5 Pro",
                "slug": "macbook-pro-16-m5-pro",
                "brand": "apple",
                "category": "laptops",
                "description": "Supercharged by the M5 Pro chip. Liquid Retina XDR display, up to 22 hours battery life, and groundbreaking performance.",
                "short_description": "Apple's pro laptop with M5 Pro chip",
                "image_url": "https://dummyjson.com/image/400x400/2d2d2d/ffffff?text=MacBook+Pro",
                "specifications": {"Display": "16.2-inch Liquid Retina XDR", "Chip": "M5 Pro", "RAM": 36, "Storage": "512GB SSD", "Battery": "22 hours", "Weight": "2.14kg", "Ports": "3x Thunderbolt 5, HDMI, SD, MagSafe"},
                "features": ["M5 Pro Chip", "Liquid Retina XDR", "22hr Battery", "Thunderbolt 5", "ProMotion 120Hz", "Studio-quality Speakers"],
                "tags": ["laptop", "apple", "macbook", "pro", "programming"],
                "average_rating": 4.8,
                "total_reviews": 1543,
            },
            {
                "name": "Dell XPS 15 (2026)",
                "slug": "dell-xps-15-2026",
                "brand": "dell",
                "category": "laptops",
                "description": "Infinity Edge OLED display, Intel Ultra 9, 32GB RAM. The ultimate Windows productivity machine.",
                "short_description": "Dell's premium ultrabook with OLED display",
                "image_url": "https://dummyjson.com/image/400x400/1e3a5f/ffffff?text=Dell+XPS+15",
                "specifications": {"Display": "15.6-inch 3.5K OLED", "Chip": "Intel Core Ultra 9 285H", "RAM": 32, "Storage": "1TB SSD", "Battery": "13 hours", "GPU": "NVIDIA RTX 4070", "Weight": "1.86kg"},
                "features": ["3.5K OLED Display", "Intel Ultra 9", "RTX 4070", "Thunderbolt 4", "Infinity Edge Design"],
                "tags": ["laptop", "dell", "ultrabook", "windows", "programming"],
                "average_rating": 4.5,
                "total_reviews": 892,
            },
            {
                "name": "HP Spectre x360 16",
                "slug": "hp-spectre-x360-16",
                "brand": "hp",
                "category": "laptops",
                "description": "2-in-1 convertible with 3K+ OLED display, Intel Core Ultra, and premium gem-cut design.",
                "short_description": "HP's premium 2-in-1 convertible",
                "image_url": "https://dummyjson.com/image/400x400/333366/ffffff?text=HP+Spectre",
                "specifications": {"Display": "16-inch 3K+ OLED Touch", "Chip": "Intel Core Ultra 7 265H", "RAM": 32, "Storage": "1TB SSD", "Battery": "17 hours", "Weight": "1.95kg"},
                "features": ["3K+ OLED Touchscreen", "360° Hinge", "Stylus Support", "17hr Battery", "Gem-cut Design"],
                "tags": ["laptop", "hp", "2-in-1", "convertible", "touchscreen"],
                "average_rating": 4.3,
                "total_reviews": 634,
            },
            # Shoes
            {
                "name": "Nike Air Max 270 React",
                "slug": "nike-air-max-270-react",
                "brand": "nike",
                "category": "shoes",
                "description": "Iconic Air Max cushioning meets React foam for all-day comfort. Lightweight, breathable, and stylish.",
                "short_description": "Nike's iconic Air Max with React foam",
                "image_url": "https://dummyjson.com/image/400x400/111111/ffffff?text=Nike+Air+Max",
                "specifications": {"Type": "Running/Lifestyle", "Sole": "Air Max + React", "Upper": "Mesh", "Closure": "Lace-up", "Weight": "310g"},
                "features": ["Air Max Cushioning", "React Foam", "Breathable Mesh", "Lightweight Design", "Rubber Outsole"],
                "tags": ["shoes", "nike", "running", "lifestyle", "sneakers"],
                "average_rating": 4.4,
                "total_reviews": 5621,
            },
            {
                "name": "Adidas Ultraboost 24",
                "slug": "adidas-ultraboost-24",
                "brand": "adidas",
                "category": "shoes",
                "description": "Legendary comfort redefined. Light BOOST midsole, Primeknit+ upper, and Continental rubber outsole.",
                "short_description": "Adidas legendary comfort running shoe",
                "image_url": "https://dummyjson.com/image/400x400/1a1a1a/ffffff?text=Ultraboost+24",
                "specifications": {"Type": "Running", "Sole": "BOOST + LEP", "Upper": "Primeknit+", "Closure": "Lace-up", "Weight": "298g"},
                "features": ["Light BOOST Midsole", "Primeknit+ Upper", "Continental Rubber", "Torsion System", "Recycled Materials"],
                "tags": ["shoes", "adidas", "running", "ultraboost"],
                "average_rating": 4.5,
                "total_reviews": 4832,
            },
            # Clothing
            {
                "name": "Allen Solly Slim Fit Oxford Shirt",
                "slug": "allen-solly-slim-fit-oxford-shirt",
                "brand": "allen-solly",
                "category": "clothing",
                "description": "Classic Oxford weave cotton shirt with a modern slim fit. Perfect for office wear and semi-formal occasions.",
                "short_description": "Classic slim fit cotton Oxford shirt",
                "image_url": "https://dummyjson.com/image/400x400/4a6fa5/ffffff?text=Allen+Solly+Shirt",
                "specifications": {"Material": "100% Cotton Oxford", "Fit": "Slim Fit", "Collar": "Button Down", "Sleeve": "Full Sleeve", "Care": "Machine Washable"},
                "features": ["Premium Cotton", "Slim Fit Cut", "Wrinkle Resistant", "Button Down Collar", "Multiple Colors"],
                "tags": ["shirt", "formal", "cotton", "slim-fit", "office"],
                "average_rating": 4.2,
                "total_reviews": 2341,
            },
            {
                "name": "US Polo Assn Classic Polo T-Shirt",
                "slug": "us-polo-classic-polo-tshirt",
                "brand": "us-polo",
                "category": "clothing",
                "description": "Timeless polo shirt with signature logo. Pique cotton fabric ensures breathability and comfort.",
                "short_description": "Classic pique cotton polo shirt",
                "image_url": "https://dummyjson.com/image/400x400/2d5a27/ffffff?text=US+Polo+Shirt",
                "specifications": {"Material": "100% Pique Cotton", "Fit": "Regular Fit", "Collar": "Ribbed Polo", "Sleeve": "Short Sleeve", "Care": "Machine Washable"},
                "features": ["Pique Cotton", "Ribbed Collar", "Signature Logo", "Breathable Fabric", "Classic Fit"],
                "tags": ["tshirt", "polo", "casual", "cotton"],
                "average_rating": 4.1,
                "total_reviews": 1876,
            },
            # Headphones
            {
                "name": "Sony WH-1000XM6",
                "slug": "sony-wh-1000xm6",
                "brand": "sony",
                "category": "headphones",
                "description": "Industry-leading noise cancellation with 40-hour battery, Hi-Res audio, and multipoint connectivity.",
                "short_description": "Sony's flagship ANC headphones",
                "image_url": "https://dummyjson.com/image/400x400/2a2a2a/ffffff?text=Sony+XM6",
                "specifications": {"Type": "Over-ear", "ANC": "HD Noise Cancelling V3", "Battery": "40 hours", "Driver": "40mm", "Codecs": "LDAC, AAC, SBC", "Weight": "250g"},
                "features": ["Industry-leading ANC", "40hr Battery", "Hi-Res Audio", "Multipoint Connection", "Speak-to-Chat", "DSEE Extreme"],
                "tags": ["headphones", "sony", "anc", "wireless", "premium"],
                "average_rating": 4.7,
                "total_reviews": 3456,
            },
            {
                "name": "Bose QuietComfort Ultra",
                "slug": "bose-quietcomfort-ultra",
                "brand": "bose",
                "category": "headphones",
                "description": "Immersive audio with Bose Immersive Audio, CustomTune, and world-class noise cancellation.",
                "short_description": "Bose premium ANC headphones",
                "image_url": "https://dummyjson.com/image/400x400/3d3d3d/ffffff?text=Bose+QC+Ultra",
                "specifications": {"Type": "Over-ear", "ANC": "Quiet Mode", "Battery": "24 hours", "Driver": "35mm", "Codecs": "aptX Adaptive, AAC, SBC", "Weight": "250g"},
                "features": ["Bose Immersive Audio", "CustomTune EQ", "World-class ANC", "24hr Battery", "Plush Cushions"],
                "tags": ["headphones", "bose", "anc", "wireless", "premium"],
                "average_rating": 4.6,
                "total_reviews": 2134,
            },
            # Watches
            {
                "name": "Apple Watch Ultra 3",
                "slug": "apple-watch-ultra-3",
                "brand": "apple",
                "category": "watches",
                "description": "The most rugged Apple Watch. Titanium case, precision dual-frequency GPS, and underwater capabilities.",
                "short_description": "Apple's rugged adventure smartwatch",
                "image_url": "https://dummyjson.com/image/400x400/ff6600/ffffff?text=Watch+Ultra+3",
                "specifications": {"Display": "49mm Always-On Retina LTPO3", "Case": "Titanium", "Battery": "72 hours", "Water": "100m", "GPS": "Dual-frequency L1+L5", "Chip": "S10"},
                "features": ["Titanium Case", "72hr Battery", "Dual-frequency GPS", "100m Water Resistant", "Action Button", "Night Mode"],
                "tags": ["watch", "smartwatch", "apple", "adventure", "fitness"],
                "average_rating": 4.8,
                "total_reviews": 987,
            },
            {
                "name": "Samsung Galaxy Watch 7 Ultra",
                "slug": "samsung-galaxy-watch-7-ultra",
                "brand": "samsung",
                "category": "watches",
                "description": "Premium Titanium smartwatch with dual-frequency GPS, advanced health monitoring, and Wear OS.",
                "short_description": "Samsung's premium Titanium smartwatch",
                "image_url": "https://dummyjson.com/image/400x400/555555/ffffff?text=Galaxy+Watch+7",
                "specifications": {"Display": "47mm Super AMOLED", "Case": "Titanium", "Battery": "60 hours", "Water": "100m", "GPS": "Dual-frequency", "OS": "Wear OS 5"},
                "features": ["Titanium Grade 4", "BioActive Sensor", "Dual-frequency GPS", "100m WR", "Wear OS 5"],
                "tags": ["watch", "smartwatch", "samsung", "fitness"],
                "average_rating": 4.5,
                "total_reviews": 743,
            },
        ]

        platforms = ["amazon", "flipkart", "myntra", "ajio", "croma", "reliance_digital", "brand_store"]

        products = {}
        for prod_data in products_data:
            brand_slug = prod_data.pop("brand")
            cat_slug = prod_data.pop("category")

            base_price = random.uniform(50, 2000)
            if "iphone" in prod_data["slug"] or "macbook" in prod_data["slug"]:
                base_price = random.uniform(999, 1599)
            elif "galaxy" in prod_data["slug"] and "watch" not in prod_data["slug"]:
                base_price = random.uniform(899, 1399)
            elif "oneplus" in prod_data["slug"]:
                base_price = random.uniform(599, 999)
            elif "xps" in prod_data["slug"] or "spectre" in prod_data["slug"]:
                base_price = random.uniform(1099, 1899)
            elif "air-max" in prod_data["slug"] or "ultraboost" in prod_data["slug"]:
                base_price = random.uniform(120, 220)
            elif "shirt" in prod_data["slug"] or "polo" in prod_data["slug"]:
                base_price = random.uniform(29, 79)
            elif "xm6" in prod_data["slug"] or "quietcomfort" in prod_data["slug"]:
                base_price = random.uniform(299, 429)
            elif "watch" in prod_data["slug"]:
                base_price = random.uniform(399, 849)

            product = Product(
                **prod_data,
                brand_id=brands[brand_slug].id,
                category_id=categories[cat_slug].id,
                current_best_price=round(base_price * 0.92, 2),
                lowest_price=round(base_price * 0.85, 2),
                highest_price=round(base_price * 1.1, 2),
                deal_score=round(random.uniform(65, 98), 1),
            )
            db.add(product)
            db.flush()
            products[product.slug] = product

            # ─── Prices across platforms ─────────────────────
            best_price = float('inf')
            best_platform = None
            relevant_platforms = random.sample(platforms, k=random.randint(3, 6))

            for platform in relevant_platforms:
                variation = random.uniform(0.88, 1.12)
                price_val = round(base_price * variation, 2)
                original_price = round(price_val * random.uniform(1.05, 1.35), 2)
                discount = round(((original_price - price_val) / original_price) * 100, 1)

                if price_val < best_price:
                    best_price = price_val
                    best_platform = platform

                price = Price(
                    product_id=product.id,
                    platform=platform,
                    price=price_val,
                    original_price=original_price,
                    discount_percentage=discount,
                    url=f"https://{platform}.com/product/{product.slug}",
                    is_available=True,
                    delivery_days=random.randint(1, 7),
                    delivery_cost=round(random.choice([0, 0, 0, 4.99, 9.99]), 2),
                    seller_name=f"{platform.replace('_', ' ').title()} Official",
                    seller_rating=round(random.uniform(3.8, 4.9), 1),
                    is_best_deal=False,
                )
                db.add(price)

            # Update product best price
            product.current_best_price = round(best_price, 2)
            product.current_best_platform = best_platform

            # Mark best deal
            db.flush()
            best_price_obj = (
                db.query(Price)
                .filter(Price.product_id == product.id)
                .order_by(Price.price.asc())
                .first()
            )
            if best_price_obj:
                best_price_obj.is_best_deal = True

            # ─── Price History (90 days) ─────────────────────
            now = datetime.now(timezone.utc)
            for day in range(90, 0, -1):
                date = now - timedelta(days=day)
                for plat in random.sample(relevant_platforms, k=min(2, len(relevant_platforms))):
                    history_price = round(base_price * random.uniform(0.85, 1.15), 2)
                    ph = PriceHistory(
                        product_id=product.id,
                        platform=plat,
                        price=history_price,
                        recorded_at=date,
                    )
                    db.add(ph)

            # ─── Reviews ─────────────────────────────────────
            review_sources = ["amazon", "flipkart", "youtube", "reddit", "tech_blog"]
            sample_pros = [
                "Excellent build quality", "Great performance", "Beautiful display",
                "Long battery life", "Good camera", "Fast charging", "Premium feel",
                "Comfortable fit", "Great value", "Smooth experience",
                "Durable material", "Lightweight", "Good color accuracy",
            ]
            sample_cons = [
                "Slightly expensive", "No charger in box", "Average battery",
                "Heats up during gaming", "Bulky design", "Limited color options",
                "No headphone jack", "Slow software updates", "Average speakers",
            ]

            for i in range(random.randint(5, 15)):
                rating = round(random.uniform(3.0, 5.0), 1)
                review = Review(
                    product_id=product.id,
                    platform=random.choice(relevant_platforms),
                    source=random.choice(review_sources),
                    reviewer_name=f"User{random.randint(1000, 9999)}",
                    rating=rating,
                    title=random.choice([
                        "Great product!", "Worth the money", "Decent purchase",
                        "Love it!", "Good but could be better", "Amazing quality",
                        "Highly recommended", "Mixed feelings", "Exceeded expectations",
                    ]),
                    content=f"{'Great' if rating >= 4 else 'Decent'} product overall. {'Highly recommend!' if rating >= 4.5 else 'Good value for money.' if rating >= 3.5 else 'Has some issues.'}",
                    pros=random.sample(sample_pros, k=random.randint(2, 4)),
                    cons=random.sample(sample_cons, k=random.randint(1, 3)),
                    is_verified=random.choice([True, True, True, False]),
                    helpful_count=random.randint(0, 200),
                    sentiment_score=round((rating - 3) / 2, 2),  # Normalize to -1 to 1
                    review_date=now - timedelta(days=random.randint(1, 180)),
                )
                db.add(review)

        print("  ✅ Products, prices, price history, and reviews created")

        # ─── Deals ──────────────────────────────────────────
        for slug, product in products.items():
            if random.random() > 0.4:  # 60% of products have deals
                platform = random.choice(platforms)
                original = product.highest_price or product.current_best_price * 1.2
                deal_price = round(product.current_best_price * random.uniform(0.8, 0.95), 2)
                discount = round(((original - deal_price) / original) * 100, 1)

                deal = Deal(
                    product_id=product.id,
                    platform=platform,
                    title=f"🔥 {discount:.0f}% OFF on {product.name}!",
                    description=f"Limited time deal on {product.name}. Save big on {platform.replace('_', ' ').title()}!",
                    deal_price=deal_price,
                    original_price=round(original, 2),
                    discount_percentage=discount,
                    deal_score=round(random.uniform(60, 98), 1),
                    is_fake_discount=random.random() < 0.1,
                    real_market_price=round(product.current_best_price, 2),
                    url=f"https://{platform}.com/deal/{product.slug}",
                    starts_at=now - timedelta(days=random.randint(0, 3)),
                    expires_at=now + timedelta(days=random.randint(1, 14)),
                    status="active",
                )
                db.add(deal)

        print("  ✅ Deals created")

        # ─── Comparisons ────────────────────────────────────
        comparison_pairs = [
            ("iphone-17-pro-max", "samsung-galaxy-s26-ultra", True),
            ("nike-air-max-270-react", "adidas-ultraboost-24", True),
            ("allen-solly-slim-fit-oxford-shirt", "us-polo-classic-polo-tshirt", True),
            ("sony-wh-1000xm6", "bose-quietcomfort-ultra", True),
            ("macbook-pro-16-m5-pro", "dell-xps-15-2026", True),
            ("apple-watch-ultra-3", "samsung-galaxy-watch-7-ultra", False),
        ]

        for slug1, slug2, is_trending in comparison_pairs:
            p1 = products.get(slug1)
            p2 = products.get(slug2)
            if p1 and p2:
                winner = p1 if (p1.average_rating or 0) >= (p2.average_rating or 0) else p2
                comp = Comparison(
                    slug=f"{slug1}-vs-{slug2}",
                    title=f"{p1.name} vs {p2.name}",
                    product_ids=[p1.id, p2.id],
                    winner_id=winner.id,
                    ai_summary=f"In the battle between {p1.name} and {p2.name}, **{winner.name}** edges ahead with a rating of {winner.average_rating}/5 and stronger overall performance.",
                    feature_scores={"Rating": {p1.id: p1.average_rating, p2.id: p2.average_rating}},
                    view_count=random.randint(100, 5000),
                    is_trending=is_trending,
                )
                db.add(comp)

        print("  ✅ Comparisons created")

        # ─── Notifications for demo user ─────────────────────
        demo_notifications = [
            {"type": "price_drop", "title": "Price Drop Alert! 🔥", "message": "iPhone 17 Pro Max dropped $100 on Flipkart! Now available at $999.", "data": {"product_slug": "iphone-17-pro-max"}},
            {"type": "new_deal", "title": "New Deal Found! 💰", "message": "30% off on Sony WH-1000XM6 headphones on Amazon.", "data": {"product_slug": "sony-wh-1000xm6"}},
            {"type": "better_deal", "title": "Better Deal Detected! ⚡", "message": "Nike Air Max 270 is $20 cheaper on Myntra than Amazon.", "data": {"product_slug": "nike-air-max-270-react"}},
        ]

        for notif_data in demo_notifications:
            notif = Notification(user_id=demo_user.id, **notif_data)
            db.add(notif)

        print("  ✅ Notifications created")

        db.commit()
        print("\n🎉 Database seeded successfully!")
        print(f"  → {len(products)} products")
        print(f"  → {len(brands_data)} brands")
        print(f"  → {len(categories_data)} categories")
        print(f"  → 2 users (admin + demo)")
        print(f"  → {len(comparison_pairs)} comparisons")
        print("\n📧 Login credentials:")
        print("  Admin: admin@brandbattle.com / admin123456")
        print("  Demo:  demo@brandbattle.com / demo123456")

    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding database: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()

"""
Flipkart Product Scraper - Updated with correct CSS selectors
Scrapes real product data and saves to flipkart_products.csv
"""
# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

import csv
import time
import random
import re
import os

import requests
from bs4 import BeautifulSoup

HEADERS_LIST = [
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept-Language": "en-IN,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Referer": "https://www.flipkart.com/",
    },
    {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    },
]

BASE_URL = "https://www.flipkart.com"

SEARCH_QUERIES = [
    ("smartphones",    "smartphone"),
    ("laptops",        "laptop"),
    ("headphones",     "headphones"),
    ("shoes",          "running shoes men"),
    ("watches",        "smartwatch"),
    ("televisions",    "4k television"),
    ("clothing",       "men formal shirt"),
    ("tablets",        "android tablet"),
    ("cameras",        "dslr camera"),
    ("gaming",         "gaming keyboard"),
]


def clean_price(text):
    if not text:
        return None
    digits = re.sub(r"[^\d]", "", text.replace(",", ""))
    return float(digits) if digits else None


def clean_rating(text):
    if not text:
        return None
    m = re.search(r"[\d.]+", text)
    return float(m.group()) if m else None


def clean_reviews(text):
    if not text:
        return 0
    # "5,901 Ratings & 351 Reviews" -> 5901
    m = re.search(r"([\d,]+)\s*Ratings", text)
    if m:
        return int(m.group(1).replace(",", ""))
    m2 = re.search(r"([\d,]+)", text)
    return int(m2.group(1).replace(",", "")) if m2 else 0


def scrape_search_page(session, query, category, page=1):
    url = f"{BASE_URL}/search?q={requests.utils.quote(query)}&page={page}"
    products = []

    try:
        resp = session.get(url, timeout=15)
        resp.raise_for_status()
    except Exception as e:
        print(f"  Request failed: {e}")
        return products

    soup = BeautifulSoup(resp.text, "html.parser")
    cards = soup.select("div[data-id]")
    print(f"  Found {len(cards)} cards for '{query}' page {page}")

    for card in cards:
        try:
            # ---- Name (RG5Slk=24-grid, RGLWAk=40-grid, atJtCj=fashion) ----
            name_el = (
                card.select_one("div.RG5Slk")
                or card.select_one("div.RGLWAk")
                or card.select_one("a.atJtCj")
                or card.select_one("div.KzDlHZ")
                or card.select_one("a.s1Q9rs")
                or card.select_one("div._4rR01T")
                or card.select_one("a.IRpwTa")
            )
            # For fashion cards, prepend brand name (div.Fo1I0b)
            brand_el = card.select_one("div.Fo1I0b")
            brand_prefix = brand_el.get_text(strip=True) + " " if brand_el else ""
            name = name_el.get_text(strip=True) if name_el else None
            if name and brand_prefix and not name.lower().startswith(brand_prefix.lower().strip()):
                name = brand_prefix + name
            if not name or len(name) < 3:
                continue

            # ---- Price (class hZ3P6w DeU9vF) ----
            price_el = (
                card.select_one("div.hZ3P6w")
                or card.select_one("div._30jeq3")
                or card.select_one("div.Nx9bqj")
                or card.select_one("div._1_WHN1")
            )
            price = clean_price(price_el.get_text() if price_el else None)

            # ---- Original price (class kRYCnD) ----
            orig_el = (
                card.select_one("div.kRYCnD")
                or card.select_one("div._3I9_wc")
                or card.select_one("div.yRaY8j")
            )
            orig_price = clean_price(orig_el.get_text() if orig_el else None)
            if orig_price is None:
                orig_price = price

            # ---- Discount (class HQe8jr) ----
            disc_el = (
                card.select_one("div.HQe8jr")
                or card.select_one("div._3Ay6Sb")
                or card.select_one("div.UkUFwK")
            )
            discount = clean_price(disc_el.get_text() if disc_el else None) or 0

            # ---- Rating (class MKiFS6) ----
            rating_el = (
                card.select_one("div.MKiFS6")
                or card.select_one("div._3LWZlK")
                or card.select_one("div.XQDdHH")
            )
            rating = clean_rating(rating_el.get_text() if rating_el else None) or 0.0

            # ---- Reviews (class PvbNMB) ----
            reviews_el = (
                card.select_one("span.PvbNMB")
                or card.select_one("span._2_R_DZ")
                or card.select_one("span.Wphh3N")
            )
            reviews = clean_reviews(reviews_el.get_text() if reviews_el else "")

            # ---- Image ----
            img_el = (
                card.select_one("img.UCc1lI")
                or card.select_one("img.MZeksS")
                or card.select_one("img._396cs4")
                or card.select_one("img._2r_T1I")
                or card.select_one("img")
            )
            image = ""
            if img_el:
                image = img_el.get("src") or img_el.get("data-src") or ""
            if image.startswith("//"):
                image = "https:" + image

            # ---- Upgrade image quality (312->400) ----
            image = image.replace("/312/312/", "/400/400/")

            # ---- Link (k7wcnx=24-grid, pIpigb=40-grid, CIaYa1=fashion) ----
            link_el = (
                card.select_one("a.k7wcnx")
                or card.select_one("a.CIaYa1")
                or card.select_one("a.pIpigb")
                or card.select_one("a.fb4uj3")
                or card.select_one("a._1fQZEK")
                or card.select_one("a.s1Q9rs")
                or card.select_one("a[href]")
            )
            link = ""
            if link_el and link_el.get("href"):
                href = link_el["href"]
                link = href if href.startswith("http") else BASE_URL + href

            # ---- Specs bullet points ----
            spec_items = card.select("li.DTBslk") or card.select("li._21lJbe") or card.select("li")
            specs = " | ".join(li.get_text(strip=True) for li in spec_items[:4])

            if price and price > 0:
                products.append({
                    "name": name,
                    "category": category,
                    "price_inr": price,
                    "original_price_inr": orig_price or price,
                    "discount_percent": discount,
                    "rating": min(rating, 5.0),
                    "total_reviews": reviews,
                    "image_url": image,
                    "flipkart_url": link,
                    "specs": specs,
                    "platform": "flipkart",
                })

        except Exception:
            continue

    return products


def scrape_all():
    all_products = []
    session = requests.Session()
    session.headers.update(HEADERS_LIST[0])

    for category, query in SEARCH_QUERIES:
        print(f"\nScraping: {category} ('{query}')")
        for page in range(1, 4):  # 3 pages per category
            products = scrape_search_page(session, query, category, page)
            all_products.extend(products)
            print(f"  Got {len(products)} products (page {page}), total so far: {len(all_products)}")
            time.sleep(random.uniform(1.2, 2.5))

        session.headers.update(random.choice(HEADERS_LIST))

    return all_products


def save_csv(products, filepath):
    if not products:
        print("No products to save!")
        return

    fieldnames = [
        "name", "category", "price_inr", "original_price_inr",
        "discount_percent", "rating", "total_reviews",
        "image_url", "flipkart_url", "specs", "platform"
    ]

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for p in products:
            writer.writerow({k: p.get(k, "") for k in fieldnames})

    print(f"\nSaved {len(products)} products to {filepath}")


if __name__ == "__main__":
    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "flipkart_products.csv")
    print("Starting Flipkart scraper...")
    products = scrape_all()
    print(f"\nTotal scraped: {len(products)} products")
    save_csv(products, out_path)
    print("Done!")

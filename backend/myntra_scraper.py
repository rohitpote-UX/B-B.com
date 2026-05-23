"""
Myntra Product Scraper - Playwright with stealth + correct DOM selectors
Selectors confirmed via live browser inspection.
"""
# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

import csv
import time
import random
import re
import os

from playwright.sync_api import sync_playwright

OUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "myntra_products.csv")

# Category slug -> display name mapping
SEARCH_CATEGORIES = [
    ("shirts",              "Clothing"),
    ("tshirts",             "Clothing"),
    ("jeans",               "Clothing"),
    ("kurtas",              "Clothing"),
    ("dresses",             "Clothing"),
    ("jackets",             "Clothing"),
    ("casual-shoes",        "Shoes"),
    ("sports-shoes",        "Shoes"),
    ("sneakers",            "Shoes"),
    ("heels",               "Shoes"),
    ("watches",             "Watches"),
    ("sunglasses",          "Accessories"),
    ("handbags",            "Accessories"),
    ("backpacks",           "Accessories"),
    ("perfumes",            "Beauty"),
]

JS_EXTRACT = """
() => {
    const cards = document.querySelectorAll('li.product-base');
    return Array.from(cards).map(card => {
        const brandEl = card.querySelector('.product-brand');
        const productEl = card.querySelector('.product-product');
        const priceEl = card.querySelector('.product-discountedPrice');
        const origEl = card.querySelector('.product-strike');
        const discEl = card.querySelector('.product-discountPercentage');
        const ratingSpans = card.querySelectorAll('.product-ratingsContainer span');
        const reviewEl = card.querySelector('.product-ratingsCount');
        const linkEl = card.querySelector('a[href]');

        // ── Multi-strategy image extraction ──
        // Myntra lazy-loads images. Try every known attribute/source.
        let image = '';

        // Strategy 1: <picture><source srcset="..."> (highest quality)
        const sourceEl = card.querySelector('picture source');
        if (sourceEl) {
            const srcset = sourceEl.getAttribute('srcset') || sourceEl.getAttribute('data-srcset') || '';
            if (srcset) {
                // srcset format: "url1 1x, url2 2x" or "url1 220w, url2 540w"
                // Split by comma, take the last entry (highest res)
                const parts = srcset.trim().split(',').map(s => s.trim().split(/\s+/)[0]).filter(Boolean);
                if (parts.length > 0) image = parts[parts.length - 1];
            }
        }

        // Strategy 2: <img> inside card — check src, then data-src
        if (!image) {
            const imgEl = card.querySelector('img.img-responsive') || card.querySelector('picture img') || card.querySelector('img');
            if (imgEl) {
                image = imgEl.src ||
                        imgEl.getAttribute('data-src') ||
                        imgEl.getAttribute('data-lazy-src') ||
                        imgEl.getAttribute('data-original') || '';
                // If src is a data-URI or blank-pixel, ignore it
                if (image && (image.startsWith('data:') || image.length < 20)) image = '';
                // Also check srcset on the img tag
                if (!image) {
                    const imgSrcset = imgEl.getAttribute('srcset') || imgEl.getAttribute('data-srcset') || '';
                    if (imgSrcset) {
                        const parts = imgSrcset.trim().split(',').map(s => s.trim().split(/\s+/)[0]).filter(Boolean);
                        if (parts.length > 0) image = parts[parts.length - 1];
                    }
                }
            }
        }

        // Strategy 3: look for any attribute containing a myntassets URL
        if (!image) {
            const allEls = card.querySelectorAll('[src*="myntassets"], [data-src*="myntassets"], [srcset*="myntassets"]');
            if (allEls.length > 0) {
                const el = allEls[0];
                image = el.getAttribute('src') || el.getAttribute('data-src') || '';
                if (!image) {
                    const s = el.getAttribute('srcset') || '';
                    if (s) image = s.trim().split(',')[0].trim().split(/\s+/)[0];
                }
            }
        }

        // Rating: first span in ratingsContainer
        let rating = '';
        if (ratingSpans.length > 0) rating = ratingSpans[0].innerText.trim();

        // Review count
        let reviews = '';
        if (reviewEl) {
            reviews = reviewEl.innerText.replace('|', '').trim();
        }

        return {
            brand: brandEl ? brandEl.innerText.trim() : '',
            product: productEl ? productEl.innerText.trim() : '',
            price: priceEl ? priceEl.innerText.trim() : '',
            orig: origEl ? origEl.innerText.trim() : '',
            discount: discEl ? discEl.innerText.trim() : '',
            rating: rating,
            reviews: reviews,
            image: image,
            link: linkEl ? linkEl.href : '',
        };
    });
}
"""


def clean_price(text):
    if not text:
        return None
    digits = re.sub(r"[^\d]", "", str(text).replace(",", ""))
    return float(digits) if digits else None


def clean_reviews(text):
    """Parse '1.6k' -> 1600, '23,456' -> 23456"""
    if not text:
        return 0
    text = text.strip().lower().replace(",", "")
    m = re.search(r"([\d.]+)k", text)
    if m:
        return int(float(m.group(1)) * 1000)
    m2 = re.search(r"[\d]+", text)
    return int(m2.group()) if m2 else 0


def upgrade_image(url):
    """Upgrade Myntra image to higher resolution and ensure HTTPS."""
    if not url:
        return url
    # Enforce HTTPS
    if url.startswith('http://'):
        url = 'https://' + url[7:]
    # Replace w_210/w_500 sizing with w_720 for HD quality
    url = re.sub(r'w_\d+', 'w_720', url)
    # Remove DPR scaling (let browser handle it)
    url = re.sub(r'dpr_[\d.]+', 'dpr_1.0', url)
    # Convert f_webp to f_auto for broader browser support
    url = re.sub(r'f_webp', 'f_auto', url)
    # Boost quality from q_60 to q_85
    url = re.sub(r'q_\d+', 'q_85', url)
    return url


def scrape_category(page, slug, cat_name):
    products = []
    url = f"https://www.myntra.com/{slug}"
    print(f"  -> {url}")

    # Retry up to 2 times on navigation failure
    for attempt in range(2):
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=35000)
            break  # success
        except Exception as e:
            print(f"  Navigation attempt {attempt+1} failed: {str(e)[:80]}")
            if attempt == 1:
                return products  # give up after 2 tries
            time.sleep(5)

    # Wait for product listing to appear
    try:
        page.wait_for_selector("li.product-base", timeout=12000)
    except Exception:
        print(f"  No products found (selector timeout)")
        return products

    # ── Slow row-by-row scroll to trigger IntersectionObserver lazy loading ──
    # Myntra uses intersection observer — we must scroll past each image for it to load
    try:
        page_height = page.evaluate("document.body.scrollHeight")
        viewport_h  = page.evaluate("window.innerHeight")
        step = max(200, viewport_h // 3)   # scroll 1/3 viewport at a time
        pos = 0
        while pos < page_height:
            page.evaluate(f"window.scrollTo(0, {pos})")
            time.sleep(0.25)               # short pause per step
            pos += step
        # Final scroll to bottom and back to top
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(1.5)
        page.evaluate("window.scrollTo(0, 0)")
        time.sleep(0.5)
    except Exception as e:
        print(f"  Scroll warning: {e}")

    # Wait for at least some images to actually load their real src
    try:
        page.wait_for_selector('img[src*="myntassets"]', timeout=8000)
    except Exception:
        # Not all pages will have loaded images – continue anyway
        pass

    # Extract
    try:
        raw = page.evaluate(JS_EXTRACT)
    except Exception as e:
        print(f"  JS eval error: {e}")
        return products

    # Count how many have images for logging
    has_img = sum(1 for r in raw if r.get("image", ""))
    print(f"  Raw cards: {len(raw)} | with images: {has_img}")

    for item in raw:
        try:
            brand = item.get("brand", "").strip()
            desc = item.get("product", "").strip()
            name = f"{brand} {desc}".strip() if desc else brand
            if not name or len(name) < 3:
                continue

            price = clean_price(item.get("price"))
            if not price or price <= 0:
                continue

            orig = clean_price(item.get("orig")) or price
            rating_raw = item.get("rating", "")
            rating = float(rating_raw) if rating_raw else 0.0

            disc_text = item.get("discount", "")
            disc_m = re.search(r"(\d+)", disc_text)
            discount = int(disc_m.group(1)) if disc_m else (
                round(((orig - price) / orig) * 100) if orig > price else 0
            )

            reviews = clean_reviews(item.get("reviews", ""))
            image = upgrade_image(item.get("image", ""))
            link = item.get("link", "")
            if link and not link.startswith("http"):
                link = "https://www.myntra.com/" + link.lstrip("/")

            products.append({
                "name": name,
                "brand": brand,
                "category": cat_name,
                "price_inr": price,
                "original_price_inr": orig,
                "discount_percent": discount,
                "rating": min(rating, 5.0),
                "total_reviews": reviews,
                "image_url": image,
                "myntra_url": link,
                "platform": "myntra",
            })
        except Exception:
            continue

    return products


def scrape_all():
    all_products = []

    with sync_playwright() as p:
        # Launch with HTTP/2 disabled to bypass Akamai/Myntra bot detection
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-accelerated-2d-canvas",
                "--no-first-run",
                "--no-zygote",
                "--disable-gpu",
                "--disable-blink-features=AutomationControlled",
                "--window-size=1366,768",
                # Critical: disable HTTP/2 — Myntra's Akamai drops H2 bot connections
                "--disable-http2",
                "--disable-quic",
                "--disable-features=NetworkService,NetworkServiceInProcess",
                "--ignore-certificate-errors",
                "--ignore-ssl-errors",
            ]
        )

        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1366, "height": 768},
            locale="en-IN",
            timezone_id="Asia/Kolkata",
            extra_http_headers={
                "Accept-Language": "en-IN,en;q=0.9,hi;q=0.8",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
                "Cache-Control": "max-age=0",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
                "Upgrade-Insecure-Requests": "1",
            },
        )

        # Comprehensive webdriver / automation flag removal
        context.add_init_script("""
            // Remove automation indicators
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            Object.defineProperty(navigator, 'plugins', {get: () => [
                {name: 'Chrome PDF Plugin'}, {name: 'Chrome PDF Viewer'},
                {name: 'Native Client'}
            ]});
            Object.defineProperty(navigator, 'languages', {get: () => ['en-IN', 'en', 'hi']});
            Object.defineProperty(navigator, 'platform', {get: () => 'Win32'});
            Object.defineProperty(navigator, 'hardwareConcurrency', {get: () => 8});
            Object.defineProperty(navigator, 'deviceMemory', {get: () => 8});
            window.chrome = {
                runtime: {}, loadTimes: function(){}, csi: function(){}, app: {}
            };
            // Prevent detection via toString
            const origQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) =>
                parameters.name === 'notifications'
                    ? Promise.resolve({ state: Notification.permission })
                    : origQuery(parameters);
        """)

        # Block only heavy non-essential resources (NOT images — we need them to load)
        def block_resource(route):
            if route.request.resource_type in ("media", "font"):
                route.abort()
            else:
                route.continue_()
        context.route("**/*", block_resource)

        page = context.new_page()

        # Visit homepage with retry
        print("Visiting Myntra homepage...")
        for attempt in range(3):
            try:
                page.goto("https://www.myntra.com/", wait_until="domcontentloaded", timeout=30000)
                time.sleep(4 + attempt)
                print("  Homepage loaded OK")
                break
            except Exception as e:
                print(f"  Homepage attempt {attempt+1} failed: {str(e)[:80]}")
                if attempt == 2:
                    print("  Proceeding without homepage warm-up...")
                time.sleep(3)

        for slug, cat_name in SEARCH_CATEGORIES:
            print(f"\nScraping category: {slug} ({cat_name})")
            products = scrape_category(page, slug, cat_name)
            all_products.extend(products)
            print(f"  Got {len(products)} valid products | Total: {len(all_products)}")
            time.sleep(random.uniform(3.0, 5.0))

        browser.close()

    return all_products


def save_csv(products, filepath):
    if not products:
        print("No products to save!")
        return

    fieldnames = [
        "name", "brand", "category", "price_inr", "original_price_inr",
        "discount_percent", "rating", "total_reviews",
        "image_url", "myntra_url", "platform"
    ]
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for p in products:
            writer.writerow({k: p.get(k, "") for k in fieldnames})

    print(f"\nSaved {len(products)} products -> {filepath}")


if __name__ == "__main__":
    print("Starting Myntra Playwright scraper...")
    products = scrape_all()
    print(f"\nTotal: {len(products)} products")
    save_csv(products, OUT_PATH)
    print("Done!")

/**
 * Amazon India Product Scraper — v2 (Improved)
 * Uses Puppeteer + Stealth Plugin to bypass anti-bot protections.
 *
 * Improvements over v1:
 *   1. Parses specs directly from product title strings (RAM, Storage, Battery, etc.)
 *   2. Generates a clean short display name (strips embedded spec text from titles)
 *   3. Scrapes 2 pages per category (double the yield)
 *   4. Enriches top 15 products per category with detail page (specs, descriptions)
 *   5. More categories: Smartphones, Laptops, Headphones, Smartwatches, Tablets,
 *      Televisions, Cameras, Gaming Controllers, Speakers, Power Banks
 *   6. Better review count extraction with multiple fallback selectors
 *   7. Extracts inline bullet-point specs from search cards
 *   8. CAPTCHA / block detection with graceful skip
 *   9. Deduplicates by ASIN to prevent duplicate product entries
 *  10. Saves a detailed log alongside the CSV for debugging
 */

const fs = require('fs');
const path = require('path');
const puppeteer = require('puppeteer-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');
puppeteer.use(StealthPlugin());

const OUT_PATH = 'amazon_products.csv';
const LOG_PATH = 'amazon_scraper.log';

// ─── Categories: [searchQuery, displayCategoryName, maxDetailPages] ───
const SEARCH_CATEGORIES = [
    ["smartphones under 30000",  "Smartphones",   2],
    ["laptops",                  "Laptops",        2],
    ["wireless headphones",      "Headphones",     2],
    ["smartwatches",             "Watches",        2],
    ["tablets android",          "Tablets",        1],
    ["4k televisions 43 inch",   "Televisions",    1],
    ["bluetooth speakers",       "Speakers",       1],
    ["power banks 20000mah",     "Power Banks",    1],
    ["dslr camera",              "Cameras",        1],
    ["gaming controller ps5",    "Gaming",         1],
];

// ─── Brand Detection ───
const BRAND_MAP = {
    "iphone": "Apple", "apple": "Apple", "macbook": "Apple", "ipad": "Apple", "airpods": "Apple",
    "samsung": "Samsung", "galaxy": "Samsung",
    "oneplus": "OnePlus", "one plus": "OnePlus",
    "realme": "Realme", "narzo": "Realme",
    "xiaomi": "Xiaomi", "redmi": "Xiaomi", "poco": "Xiaomi", "mi ": "Xiaomi",
    "vivo": "Vivo", "iqoo": "iQOO",
    "oppo": "OPPO", "reno": "OPPO",
    "nokia": "Nokia",
    "nothing": "Nothing", "nothing phone": "Nothing",
    "motorola": "Motorola", "moto ": "Motorola",
    "dell": "Dell", " hp ": "HP", "lenovo": "Lenovo", "asus": "Asus",
    "acer": "Acer", "msi ": "MSI", "avita": "AVITA", "microsoft surface": "Microsoft",
    "sony": "Sony", "bose": "Bose", "jbl": "JBL", "boat": "boAt",
    "sennheiser": "Sennheiser", "audio-technica": "Audio-Technica",
    "noise": "Noise", "fire-boltt": "Fire-Boltt", "amazfit": "Amazfit",
    "garmin": "Garmin", "fastrack": "Fastrack", "titan": "Titan",
    "marshall": "Marshall", "anker": "Anker", "soundcore": "Anker",
    "boult": "Boult", "zebronics": "Zebronics", "portronics": "Portronics",
    "lg ": "LG", "tcl": "TCL", "hisense": "Hisense", "vu ": "Vu",
    "canon": "Canon", "nikon": "Nikon", "fujifilm": "Fujifilm",
    "gopro": "GoPro", "dji": "DJI",
    "playstation": "Sony", "dualsense": "Sony",
    "xbox": "Microsoft",
    "mi power": "Xiaomi", "ambrane": "Ambrane",
};

function detectBrand(name) {
    const lower = name.toLowerCase();
    for (const [key, brand] of Object.entries(BRAND_MAP)) {
        if (lower.includes(key)) return brand;
    }
    const words = name.split(' ');
    return words[0] || 'Unknown';
}

// ─── Spec Extraction from Product Title ───
// Amazon titles pack specs like: "Samsung Galaxy M35 5G (Thunder Grey,8GB RAM,256GB Storage) | ..."
function extractSpecsFromTitle(title) {
    const specs = {};
    const lower = title.toLowerCase();

    // RAM
    const ram = title.match(/(\d+)\s*GB\s*RAM/i);
    if (ram) specs['RAM'] = `${ram[1]} GB`;

    // Storage
    const storage = title.match(/(\d+)\s*GB\s*(?:ROM|Storage|Internal)/i) ||
                    title.match(/(\d+)\s*TB\s*(?:ROM|Storage|Internal)/i);
    if (storage) specs['Storage'] = `${storage[1]} ${storage[0].includes('TB') ? 'TB' : 'GB'}`;

    // Battery
    const battery = title.match(/(\d{3,5})\s*mAh/i);
    if (battery) specs['Battery'] = `${battery[1]} mAh`;

    // Charging speed
    const charging = title.match(/(\d{2,3})W\s*(?:Fast\s*)?Charg/i);
    if (charging) specs['Fast Charging'] = `${charging[1]}W`;

    // Display size
    const display = title.match(/(\d+\.?\d*)\s*(?:inch|")\s*(?:Screen|Display|FHD|HD|AMOLED|LCD|IPS)?/i);
    if (display) specs['Display'] = `${display[1]}"`;

    // Refresh rate
    const refresh = title.match(/(\d{2,3})\s*Hz/i);
    if (refresh) specs['Refresh Rate'] = `${refresh[1]} Hz`;

    // Camera
    const camera = title.match(/(\d+)\s*MP\s*(?:Main\s*)?Camera/i);
    if (camera) specs['Camera'] = `${camera[1]} MP`;

    // Processor
    const proc = title.match(/(Snapdragon|Dimensity|Helio|Exynos|Unisoc|A1[5-9]|A[0-9]+\s*Bionic|i[3579][\s-]\d+|Ryzen\s*\d+|Core\s*i[3579]|Intel\s*\w+|AMD\s*\w+)\s*[\w\s]*/i);
    if (proc) specs['Processor'] = proc[0].trim().replace(/\s+/g, ' ').substring(0, 40);

    // 5G
    if (lower.includes('5g')) specs['Connectivity'] = '5G';

    // IP rating
    const ip = title.match(/\b(IP\d{2})\b/i);
    if (ip) specs['Water Resistance'] = ip[1].toUpperCase();

    // Screen resolution
    const res = title.match(/(FHD\+?|QHD\+?|AMOLED|Super AMOLED|OLED|QLED|4K|UHD)/i);
    if (res) specs['Display Type'] = res[1].toUpperCase().replace('AMOLED', 'AMOLED').replace('SUPER AMOLED', 'Super AMOLED');

    // OS
    if (lower.includes('windows 11')) specs['OS'] = 'Windows 11';
    else if (lower.includes('windows 10')) specs['OS'] = 'Windows 10';
    else if (lower.includes('android')) specs['OS'] = 'Android';
    else if (lower.includes('ios')) specs['OS'] = 'iOS';

    // Weight (for laptops/devices)
    const weight = title.match(/(\d+\.?\d*)\s*kg/i);
    if (weight) specs['Weight'] = `${weight[1]} kg`;

    return specs;
}

// ─── Generate Short/Clean Display Name ───
// Trims the title to a useful short name by cutting at the first '|' or '('
// and limiting length to 80 chars
function cleanName(title) {
    // Amazon titles often format as: "Product Core Name | Extra Spec | Another Spec"
    // or "Product Core Name (Color, 8GB RAM, 256GB)"
    let name = title;

    // Cut at pipe — everything after the first '|' is usually repeated spec info
    const pipeIdx = name.indexOf(' | ');
    if (pipeIdx > 20) name = name.substring(0, pipeIdx);

    // Limit to 80 chars, break at word boundary
    if (name.length > 90) {
        name = name.substring(0, 90).replace(/\s+\S*$/, '');
    }

    return name.trim();
}

// ─── Utility Functions ───
function cleanPrice(text) {
    if (!text) return null;
    const cleaned = text.replace(/[₹,\s]/g, '');
    const match = cleaned.match(/([\d.]+)/);
    return match ? parseFloat(match[1]) : null;
}

function cleanRating(text) {
    if (!text) return 0;
    const match = text.match(/([\d.]+)/);
    return match ? Math.min(parseFloat(match[1]), 5.0) : 0;
}

function cleanReviews(text) {
    if (!text) return 0;
    text = text.replace(/[,()]/g, '').trim();
    // Handle "1.2K" or "12K" formats sometimes used
    if (text.match(/\d+\.?\d*K/i)) {
        return Math.round(parseFloat(text) * 1000);
    }
    const match = text.match(/(\d+)/);
    return match ? parseInt(match[1]) : 0;
}

function upgradeImageUrl(url) {
    if (!url) return url;
    return url
        .replace(/_AC_UY\d+_/g, '_AC_UL500_')
        .replace(/_AC_UL\d+_SR\d+,\d+_/g, '_AC_UL500_')
        .replace(/_AC_US\d+_/g, '_AC_UL500_')
        .replace(/_SX\d+_SY\d+_/g, '_SL500_')
        .replace(/_SS\d+_/g, '_SL500_');
}

function extractAsin(url) {
    if (!url) return null;
    const match = url.match(/\/dp\/([A-Z0-9]{10})/);
    return match ? match[1] : null;
}

function delay(ms) {
    return new Promise(r => setTimeout(r, ms));
}

const log = [];
function logLine(msg) {
    console.log(msg);
    log.push(msg);
}

// ─── CAPTCHA / Block Detection ───
async function isBlocked(page) {
    const title = await page.title();
    const url = page.url();
    if (
        title.toLowerCase().includes('robot check') ||
        title.toLowerCase().includes('captcha') ||
        url.includes('captcha') ||
        url.includes('/errors/')
    ) {
        logLine('  ⚠️  CAPTCHA/block detected! Waiting 15 seconds and retrying...');
        return true;
    }
    return false;
}

// ─── Individual Product Detail Scraper ───
async function scrapeProductDetail(page, productUrl) {
    try {
        await page.goto(productUrl, { waitUntil: 'domcontentloaded', timeout: 25000 });
        await delay(1800 + Math.random() * 1200);

        if (await isBlocked(page)) {
            await delay(15000);
            return { description: '', specs: '{}', detailRating: '', detailReviews: '' };
        }

        const details = await page.evaluate(() => {
            let description = '';
            const specs = {};

            // Feature bullets (the main product highlights)
            const bullets = document.querySelectorAll('#feature-bullets li span.a-list-item');
            const bulletTexts = [];
            bullets.forEach(b => {
                const text = b.textContent.trim();
                if (text && text.length > 5 && !text.includes('Click here') && !text.includes('See more')) {
                    bulletTexts.push(text);
                }
            });
            if (bulletTexts.length > 0) {
                description = bulletTexts.slice(0, 5).join(' | ');
            }

            // Product description paragraph
            const aboutEl = document.querySelector('#productDescription p') ||
                             document.querySelector('#productDescription');
            if (aboutEl && aboutEl.textContent.trim().length > 10) {
                const aboutText = aboutEl.textContent.trim().substring(0, 300);
                description = description ? `${description} || ${aboutText}` : aboutText;
            }

            // Technical specifications table (multiple selectors)
            const specSelectors = [
                '#productDetails_techSpec_section_1 tr',
                '#poExpander tr',
                '.prodDetTable tr',
                '#tech-spec-table tr',
                '.a-expander-content.a-expander-partial-collapse-content tr',
            ];
            for (const sel of specSelectors) {
                document.querySelectorAll(sel).forEach(row => {
                    const th = row.querySelector('th');
                    const td = row.querySelector('td');
                    if (th && td) {
                        const key = th.textContent.trim().replace(/\s+/g, ' ');
                        const val = td.textContent.trim().replace(/\s+/g, ' ');
                        if (key && val && key.length < 60 && val.length < 200) {
                            specs[key] = val;
                        }
                    }
                });
            }

            // Detail bullets (ASIN, date, etc. — less useful but add for completeness)
            const addInfoRows = document.querySelectorAll(
                '#productDetails_detailBullets_sections1 tr, .a-keyvalue tr'
            );
            addInfoRows.forEach(row => {
                const th = row.querySelector('th, .a-span3');
                const td = row.querySelector('td, .a-span9');
                if (th && td) {
                    const key = th.textContent.trim().replace(/\s+/g, ' ');
                    const val = td.textContent.trim().replace(/\s+/g, ' ');
                    if (
                        key && val && key.length < 60 &&
                        !key.includes('ASIN') && !key.includes('Customer Reviews') &&
                        !key.includes('Best Sellers Rank')
                    ) {
                        specs[key] = val;
                    }
                }
            });

            // Ratings & reviews from detail page (often more accurate than search page)
            const overallRating = document.querySelector('#acrPopover .a-icon-alt') ||
                                  document.querySelector('[data-hook="rating-out-of-text"]');
            const totalRatings = document.querySelector('#acrCustomerReviewText') ||
                                 document.querySelector('[data-hook="total-review-count"]');

            return {
                description: description.substring(0, 600),
                specs: JSON.stringify(specs),
                detailRating: overallRating ? overallRating.textContent.trim() : '',
                detailReviews: totalRatings ? totalRatings.textContent.trim() : '',
            };
        });

        return details;
    } catch (e) {
        logLine(`    Detail page error: ${e.message.substring(0, 80)}`);
        return { description: '', specs: '{}', detailRating: '', detailReviews: '' };
    }
}

// ─── Search Results Scraper (single page) ───
async function scrapeSinglePage(page, url, category) {
    const products = [];

    try {
        await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });
    } catch (e) {
        logLine(`  Navigation error: ${e.message.substring(0, 60)}`);
        return products;
    }

    if (await isBlocked(page)) {
        await delay(15000);
        return products;
    }

    try {
        await page.waitForSelector('[data-component-type="s-search-result"]', { timeout: 15000 });
    } catch (e) {
        logLine(`  No search results found on page (selector timeout)`);
        return products;
    }

    // Scroll to load lazy images
    for (let i = 0; i < 6; i++) {
        await page.evaluate(() => window.scrollBy(0, window.innerHeight));
        await delay(600);
    }
    await page.evaluate(() => window.scrollTo(0, 0));
    await delay(400);

    const rawCards = await page.evaluate(() => {
        const cards = document.querySelectorAll('[data-component-type="s-search-result"]');
        return Array.from(cards).map(card => {
            const isAd = !!card.querySelector('.puis-sponsored-label-text');

            // Title
            const titleEl = card.querySelector('h2') || card.querySelector('.a-text-normal');
            const title = titleEl ? titleEl.textContent.trim() : '';

            // Full product URL
            const linkEl = card.querySelector('a[href*="/dp/"]') || card.querySelector('h2 a');
            let link = linkEl ? linkEl.getAttribute('href') : '';
            if (link && !link.startsWith('http')) link = 'https://www.amazon.in' + link;

            // ASIN from data attribute (more reliable)
            const asin = card.getAttribute('data-asin') || '';

            // Current price
            const priceEl =
                card.querySelector('.a-price:not(.a-text-price) .a-offscreen') ||
                card.querySelector('.a-price-whole');
            const price = priceEl ? priceEl.textContent.trim() : '';

            // Original (strikethrough) price
            const origPriceEl = card.querySelector('.a-price.a-text-price .a-offscreen');
            const origPrice = origPriceEl ? origPriceEl.textContent.trim() : '';

            // Rating — try multiple selectors
            const ratingEl =
                card.querySelector('.a-icon-alt') ||
                card.querySelector('[aria-label*="stars"]') ||
                card.querySelector('[aria-label*="out of 5"]');
            const rating = ratingEl
                ? (ratingEl.textContent || ratingEl.getAttribute('aria-label') || '')
                : '';

            // Review count — multiple selectors
            const reviewEl =
                card.querySelector('a[href*="#customerReviews"]') ||
                card.querySelector('.a-size-base.s-underline-text') ||
                card.querySelector('[aria-label*="ratings"]') ||
                card.querySelector('.a-size-small .a-link-normal') ||
                card.querySelector('[data-csa-c-type="widget"] span[aria-label]');
            const reviews = reviewEl
                ? (reviewEl.textContent.trim() || reviewEl.getAttribute('aria-label') || '')
                : '';

            // Discount badge
            const discountEl = card.querySelector('.a-letter-space + span') ||
                                card.querySelector('.s-percent-off');
            const discount = discountEl ? discountEl.textContent.trim() : '';

            // Image URL
            const imgEl = card.querySelector('.s-image') || card.querySelector('img[src*="amazon"]');
            const image = imgEl ? (imgEl.getAttribute('src') || '') : '';

            // Inline specs list (Amazon sometimes shows quick specs under title)
            const specsEl = card.querySelectorAll('.a-size-base.a-color-secondary');
            const inlineSpecs = Array.from(specsEl)
                .map(el => el.textContent.trim())
                .filter(s => s.length > 2 && s.length < 80)
                .slice(0, 5);

            return {
                title,
                link,
                asin,
                price,
                origPrice,
                rating,
                reviews,
                image,
                discount,
                inlineSpecs,
                isAd,
            };
        });
    });

    logLine(`  Raw cards extracted: ${rawCards.length}`);

    // Process and validate extracted data
    for (const item of rawCards) {
        try {
            if (!item.title || item.title.length < 5) continue;

            const price = cleanPrice(item.price);
            if (!price || price <= 0) continue;

            let origPrice = cleanPrice(item.origPrice);
            if (!origPrice || origPrice < price) origPrice = price;

            const rating = cleanRating(item.rating);
            if (rating < 2.0) continue; // skip very low-rated

            const reviews = cleanReviews(item.reviews);
            const brand = detectBrand(item.title);
            const image = upgradeImageUrl(item.image);
            const name = cleanName(item.title);
            const asin = item.asin || extractAsin(item.link);

            let discount = 0;
            const discMatch = (item.discount || '').match(/(\d+)/);
            if (discMatch) {
                discount = parseInt(discMatch[1]);
            } else if (origPrice > price) {
                discount = Math.round(((origPrice - price) / origPrice) * 100);
            }

            // Parse specs from title
            const titleSpecs = extractSpecsFromTitle(item.title);

            // Add inline spec texts as raw bullets (will be used if detail page fails)
            if (item.inlineSpecs && item.inlineSpecs.length > 0) {
                titleSpecs['_inline'] = item.inlineSpecs.join(' · ');
            }

            products.push({
                name,
                fullTitle: item.title.substring(0, 250),
                brand,
                category,
                price_inr: price,
                original_price_inr: origPrice,
                discount_percent: discount,
                rating: Math.min(rating, 5.0),
                total_reviews: reviews,
                image_url: image,
                amazon_url: item.link,
                asin: asin || '',
                description: '',
                specs: JSON.stringify(titleSpecs),
                platform: 'amazon',
                isAd: item.isAd,
            });
        } catch (e) {
            continue;
        }
    }

    return products;
}

// ─── Multi-Page Scraper ───
async function scrapeMultiplePages(page, query, category, maxPages = 2) {
    let allProducts = [];
    const seenAsins = new Set();

    for (let pageNum = 1; pageNum <= maxPages; pageNum++) {
        const url = pageNum === 1
            ? `https://www.amazon.in/s?k=${encodeURIComponent(query)}&ref=nb_sb_noss`
            : `https://www.amazon.in/s?k=${encodeURIComponent(query)}&page=${pageNum}`;

        logLine(`  → Page ${pageNum}: ${url}`);

        const pageProducts = await scrapeSinglePage(page, url, category);

        // Deduplicate by ASIN
        for (const p of pageProducts) {
            if (p.asin && seenAsins.has(p.asin)) continue;
            if (p.asin) seenAsins.add(p.asin);
            allProducts.push(p);
        }

        logLine(`    Page ${pageNum} valid products: ${pageProducts.length} | Running: ${allProducts.length}`);

        if (pageNum < maxPages) {
            await delay(4000 + Math.random() * 3000);
        }
    }

    return allProducts;
}

// ─── Enrich Top Products with Detail Page Data ───
async function enrichWithDetails(page, products, maxDetails = 15) {
    logLine(`\n📋 Enriching top ${maxDetails} products with detail page data...`);

    // Sort by reviews (most popular first), skip ads
    const sortedProducts = [...products]
        .filter(p => !p.isAd && p.rating >= 3.0)
        .sort((a, b) => b.total_reviews - a.total_reviews);

    const toEnrich = sortedProducts.slice(0, maxDetails);
    let enriched = 0;

    for (const product of toEnrich) {
        if (!product.amazon_url || product.amazon_url.includes('#')) continue;

        logLine(`  Enriching (${enriched + 1}/${toEnrich.length}): ${product.name.substring(0, 55)}...`);
        const details = await scrapeProductDetail(page, product.amazon_url);

        if (details.description) product.description = details.description;

        // Merge specs: title-extracted + detail page specs
        let existingSpecs = {};
        try { existingSpecs = JSON.parse(product.specs || '{}'); } catch {}
        let detailSpecs = {};
        try { detailSpecs = JSON.parse(details.specs || '{}'); } catch {}

        // Remove the _inline key before merging
        delete existingSpecs['_inline'];
        const mergedSpecs = { ...existingSpecs, ...detailSpecs };
        if (Object.keys(mergedSpecs).length > 0) {
            product.specs = JSON.stringify(mergedSpecs);
        }

        if (details.detailRating) {
            const r = cleanRating(details.detailRating);
            if (r > 0) product.rating = r;
        }
        if (details.detailReviews) {
            const rev = cleanReviews(details.detailReviews);
            if (rev > product.total_reviews) product.total_reviews = rev;
        }

        enriched++;
        await delay(2500 + Math.random() * 2500);
    }

    logLine(`  ✅ Enriched ${enriched} products with descriptions & specs`);
}

// ─── Main Scraper ───
async function scrapeAll() {
    logLine('═══════════════════════════════════════════════════════');
    logLine('  Amazon India Product Scraper v2 (Puppeteer + Stealth)');
    logLine('═══════════════════════════════════════════════════════');
    logLine(`  Started: ${new Date().toISOString()}`);

    const browser = await puppeteer.launch({
        headless: 'new',
        args: [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--disable-accelerated-2d-canvas',
            '--no-first-run',
            '--no-zygote',
            '--disable-gpu',
            '--window-size=1366,768',
            '--disable-blink-features=AutomationControlled',
        ],
    });

    const page = await browser.newPage();

    // Realistic browser profile
    await page.setViewport({ width: 1366, height: 768 });
    await page.setUserAgent(
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
    );
    await page.setExtraHTTPHeaders({
        'Accept-Language': 'en-IN,en;q=0.9,hi;q=0.8',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
    });

    // Block heavy resources to speed up scraping
    await page.setRequestInterception(true);
    page.on('request', req => {
        const type = req.resourceType();
        if (['stylesheet', 'font', 'media'].includes(type)) {
            req.abort();
        } else {
            req.continue();
        }
    });

    // Visit Amazon homepage first to set cookies / session
    logLine('\n🏠 Warming up with Amazon.in homepage...');
    try {
        await page.goto('https://www.amazon.in/', { waitUntil: 'domcontentloaded', timeout: 25000 });
        await delay(3500 + Math.random() * 1500);
        logLine('  Homepage loaded OK');
    } catch (e) {
        logLine(`  Homepage warning: ${e.message.substring(0, 60)}`);
    }

    let allProducts = [];

    // Scrape each category
    for (const [query, catName, maxPages] of SEARCH_CATEGORIES) {
        logLine(`\n━━━ Category: "${query}" → ${catName} (${maxPages} pages) ━━━`);
        const products = await scrapeMultiplePages(page, query, catName, maxPages);
        allProducts = allProducts.concat(products);
        logLine(`  ✓ ${catName}: ${products.length} products | Total so far: ${allProducts.length}`);

        // Anti-detection delay between categories
        await delay(3000 + Math.random() * 3000);
    }

    logLine(`\n${'━'.repeat(50)}`);
    logLine(`Total scraped from search pages: ${allProducts.length}`);

    // Enrich with detail pages — 15 per category
    if (allProducts.length > 0) {
        // Group by category and enrich top 15 of each
        const byCategory = {};
        for (const p of allProducts) {
            byCategory[p.category] = byCategory[p.category] || [];
            byCategory[p.category].push(p);
        }
        for (const [cat, prods] of Object.entries(byCategory)) {
            logLine(`\n  Enriching category: ${cat}`);
            await enrichWithDetails(page, prods, 15);
        }
    }

    await browser.close();
    return allProducts;
}

// ─── CSV Writer ───
function saveCSV(products, filepath) {
    if (products.length === 0) {
        logLine('❌ No products to save!');
        return;
    }

    const fieldnames = [
        'name', 'brand', 'category', 'price_inr', 'original_price_inr',
        'discount_percent', 'rating', 'total_reviews',
        'image_url', 'amazon_url', 'description', 'specs', 'platform',
    ];

    const escapeCSV = val => {
        if (val === null || val === undefined) return '';
        let str = String(val);
        if (str.includes(',') || str.includes('"') || str.includes('\n')) {
            return `"${str.replace(/"/g, '""')}"`;
        }
        return str;
    };

    const lines = [fieldnames.join(',')];
    for (const p of products) {
        const row = fieldnames.map(f => escapeCSV(p[f]));
        lines.push(row.join(','));
    }

    fs.writeFileSync(filepath, lines.join('\n') + '\n', 'utf-8');
    logLine(`\n✅ Saved ${products.length} products → ${filepath}`);
}

// ─── Summary Stats ───
function printStats(products) {
    logLine('\n📊 SCRAPING SUMMARY');
    logLine('─'.repeat(50));

    const byCat = {};
    const byBrand = {};
    let withDesc = 0, withSpecs = 0, withImg = 0;

    for (const p of products) {
        byCat[p.category] = (byCat[p.category] || 0) + 1;
        byBrand[p.brand] = (byBrand[p.brand] || 0) + 1;
        if (p.description) withDesc++;
        if (p.specs && p.specs !== '{}') {
            try {
                const s = JSON.parse(p.specs);
                if (Object.keys(s).length > 0) withSpecs++;
            } catch {}
        }
        if (p.image_url) withImg++;
    }

    logLine('\nBy Category:');
    for (const [cat, count] of Object.entries(byCat).sort((a, b) => b[1] - a[1])) {
        logLine(`  ${cat.padEnd(20)} ${count}`);
    }

    logLine('\nTop 15 Brands:');
    const topBrands = Object.entries(byBrand).sort((a, b) => b[1] - a[1]).slice(0, 15);
    for (const [brand, count] of topBrands) {
        logLine(`  ${brand.padEnd(20)} ${count}`);
    }

    const avgRating = (products.reduce((s, p) => s + p.rating, 0) / products.length).toFixed(2);
    logLine(`\n  Products with descriptions : ${withDesc}/${products.length}`);
    logLine(`  Products with specs        : ${withSpecs}/${products.length}`);
    logLine(`  Products with images       : ${withImg}/${products.length}`);
    logLine(`  Average rating             : ${avgRating}`);
}

// ─── Run ───
scrapeAll()
    .then(products => {
        // Filter out ads and very low quality items
        const filtered = products.filter(
            p => !p.isAd && p.rating >= 3.0 && p.image_url && p.name.length >= 8
        );

        logLine(`\nFiltered: ${products.length} → ${filtered.length} (removed ads & low quality)`);

        saveCSV(filtered, OUT_PATH);
        printStats(filtered);

        // Save log
        fs.writeFileSync(LOG_PATH, log.join('\n') + '\n', 'utf-8');

        logLine('\n🎉 Amazon scraping v2 complete!');
        logLine(`   → Run "python csv_to_demodata.py" to regenerate frontend data.`);
        logLine(`   → Log saved to: ${LOG_PATH}`);
    })
    .catch(err => {
        console.error('Fatal error:', err);
        fs.writeFileSync(LOG_PATH, log.join('\n') + '\nFATAL: ' + err.message + '\n', 'utf-8');
        process.exit(1);
    });

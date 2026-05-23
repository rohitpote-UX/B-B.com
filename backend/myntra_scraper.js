const fs = require('fs');
const puppeteer = require('puppeteer-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');
puppeteer.use(StealthPlugin());

const OUT_PATH = 'myntra_products.csv';

const SEARCH_CATEGORIES = [
    ["shirts",              "Clothing"],
    ["tshirts",             "Clothing"],
    ["jeans",               "Clothing"],
    ["kurtas",              "Clothing"],
    ["dresses",             "Clothing"],
    ["jackets",             "Clothing"],
    ["casual-shoes",        "Shoes"],
    ["sports-shoes",        "Shoes"],
    ["sneakers",            "Shoes"],
    ["heels",               "Shoes"],
    ["watches",             "Watches"],
    ["sunglasses",          "Accessories"],
    ["handbags",            "Accessories"],
    ["backpacks",           "Accessories"],
    ["perfumes",            "Beauty"]
];

function cleanPrice(text) {
    if (!text) return null;
    const digits = text.replace(/[^\d]/g, '');
    return digits ? parseFloat(digits) : null;
}

function cleanReviews(text) {
    if (!text) return 0;
    text = text.trim().toLowerCase().replace(/,/g, '');
    const m = text.match(/([\d.]+)k/);
    if (m) return parseInt(parseFloat(m[1]) * 1000);
    const m2 = text.match(/[\d]+/);
    return m2 ? parseInt(m2[0]) : 0;
}

function upgradeImage(url) {
    if (!url) return url;
    return url.replace(/w_\d+/, 'w_500').replace(/dpr_[\d.]+/, 'dpr_1.0');
}

async function scrapeCategory(page, slug, catName) {
    const url = `https://www.myntra.com/${slug}`;
    console.log(`  -> ${url}`);
    const products = [];

    try {
        await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });
    } catch (e) {
        console.log(`  Error: ${e.message}`);
        return products;
    }

    try {
        await page.waitForSelector('li.product-base', { timeout: 12000 });
    } catch (e) {
        console.log(`  No products found (selector timeout)`);
        return products;
    }

    // Scroll to trigger lazy loading
    for (let i = 0; i < 4; i++) {
        await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
        await new Promise(r => setTimeout(r, 1200));
    }
    await page.evaluate(() => window.scrollTo(0, 0));
    await new Promise(r => setTimeout(r, 500));

    const raw = await page.evaluate(() => {
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
            
            const pictureEl = card.querySelector('picture.img-responsive');
            let image = '';
            if (pictureEl) {
                const sourceEl = pictureEl.querySelector('source');
                if (sourceEl && sourceEl.srcset) {
                    const match = sourceEl.srcset.match(/(https:\/\/[^\s]+)/);
                    if (match) image = match[1];
                }
                if (!image) {
                    const imgEl = pictureEl.querySelector('img');
                    if (imgEl) image = imgEl.src || imgEl.dataset ? imgEl.dataset.src : '';
                }
            }
            if (!image) {
                const imgEl = card.querySelector('img.img-responsive') || card.querySelector('img');
                if (imgEl) image = imgEl.src || (imgEl.dataset ? imgEl.dataset.src : '');
            }

            let rating = '';
            if (ratingSpans.length > 0) rating = ratingSpans[0].innerText.trim();

            let reviews = '';
            if (reviewEl) reviews = reviewEl.innerText.replace('|', '').trim();

            return {
                brand: brandEl ? brandEl.innerText.trim() : '',
                product: productEl ? productEl.innerText.trim() : '',
                price: priceEl ? priceEl.innerText.trim() : '',
                orig: origEl ? origEl.innerText.trim() : '',
                discount: discEl ? discEl.innerText.trim() : '',
                rating: rating,
                reviews: reviews,
                image: image,
                link: linkEl ? linkEl.href : ''
            };
        });
    });

    console.log(`  Raw cards: ${raw.length}`);

    for (let item of raw) {
        try {
            const brand = item.brand;
            const desc = item.product;
            const name = desc ? `${brand} ${desc}`.trim() : brand;
            if (!name || name.length < 3) continue;

            const price = cleanPrice(item.price);
            if (!price || price <= 0) continue;

            let orig = cleanPrice(item.orig);
            if (!orig) orig = price;

            const rating = parseFloat(item.rating) || 0.0;

            let discount = 0;
            const discMatch = item.discount.match(/(\d+)/);
            if (discMatch) {
                discount = parseInt(discMatch[1]);
            } else if (orig > price) {
                discount = Math.round(((orig - price) / orig) * 100);
            }

            const reviews = cleanReviews(item.reviews);
            const image = upgradeImage(item.image);
            
            let link = item.link;
            if (link && !link.startsWith('http')) {
                link = 'https://www.myntra.com/' + link.replace(/^\//, '');
            }

            products.push({
                name, brand, category: catName, price_inr: price,
                original_price_inr: orig, discount_percent: discount,
                rating: Math.min(rating, 5.0), total_reviews: reviews,
                image_url: image, myntra_url: link, platform: 'myntra'
            });
        } catch (e) {
            continue;
        }
    }

    return products;
}

async function scrapeAll() {
    console.log("Starting Myntra Puppeteer Stealth Scraper...");
    const browser = await puppeteer.launch({
        headless: "new",
        args: [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--disable-accelerated-2d-canvas',
            '--no-first-run',
            '--no-zygote',
            '--disable-gpu',
            '--window-size=1280,900'
        ]
    });

    const page = await browser.newPage();
    await page.setViewport({ width: 1280, height: 900 });
    
    await page.setRequestInterception(true);
    page.on('request', req => {
        const type = req.resourceType();
        if (['image', 'stylesheet', 'font', 'media'].includes(type)) {
            req.abort();
        } else {
            req.continue();
        }
    });

    console.log("Visiting Myntra homepage...");
    try {
        await page.goto('https://www.myntra.com/', { waitUntil: 'domcontentloaded', timeout: 20000 });
        await new Promise(r => setTimeout(r, 2000));
        console.log("  Homepage loaded OK");
    } catch (e) {
        console.log(`  Homepage warning: ${e.message}`);
    }

    let allProducts = [];

    for (const [slug, catName] of SEARCH_CATEGORIES) {
        console.log(`\nScraping category: ${slug} (${catName})`);
        const products = await scrapeCategory(page, slug, catName);
        allProducts = allProducts.concat(products);
        console.log(`  Got ${products.length} valid products | Total: ${allProducts.length}`);
        await new Promise(r => setTimeout(r, 2000 + Math.random() * 2000));
    }

    await browser.close();
    
    return allProducts;
}

function saveCSV(products, filepath) {
    if (products.length === 0) {
        console.log("No products to save!");
        return;
    }
    
    const fieldnames = [
        "name", "brand", "category", "price_inr", "original_price_inr",
        "discount_percent", "rating", "total_reviews",
        "image_url", "myntra_url", "platform"
    ];
    
    const escapeCSV = (val) => {
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
    console.log(`\nSaved ${products.length} products -> ${filepath}`);
}

scrapeAll().then(products => {
    saveCSV(products, OUT_PATH);
}).catch(console.error);

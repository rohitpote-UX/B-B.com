const puppeteer = require('puppeteer-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');
puppeteer.use(StealthPlugin());

async function run() {
    const browser = await puppeteer.launch({
        headless: "new",
        args: ['--no-sandbox']
    });
    const page = await browser.newPage();
    await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36');
    
    console.log("Visiting Amazon...");
    await page.goto('https://www.amazon.in/s?k=smartphones', { waitUntil: 'domcontentloaded' });
    
    console.log("Extracting cards...");
    const rawCards = await page.evaluate(() => {
        const cards = document.querySelectorAll('[data-component-type="s-search-result"]');
        return Array.from(cards).slice(0, 3).map(card => {
            const isAd = card.querySelector('.puis-sponsored-label-text');
            const titleEl = card.querySelector('h2') || card.querySelector('.a-text-normal');
            const linkEl = card.querySelector('a[href*="/dp/"]') || card.querySelector('h2 a');
            const priceEl = card.querySelector('.a-price:not(.a-text-price) .a-offscreen') || card.querySelector('.a-price-whole');
            const origPriceEl = card.querySelector('.a-price.a-text-price .a-offscreen');
            const ratingEl = card.querySelector('.a-icon-alt') || card.querySelector('[aria-label*="stars"]');
            const reviewEl = card.querySelector('a[href*="#customerReviews"]') || card.querySelector('.a-size-base.s-underline-text') || card.querySelector('[aria-label*="ratings"]');
            const imgEl = card.querySelector('.s-image') || card.querySelector('img');

            return {
                title: titleEl ? titleEl.textContent.trim() : '',
                link: linkEl ? linkEl.getAttribute('href') : '',
                price: priceEl ? priceEl.textContent.trim() : '',
                origPrice: origPriceEl ? origPriceEl.textContent.trim() : '',
                rating: ratingEl ? ratingEl.textContent.trim() : '',
                reviews: reviewEl ? reviewEl.textContent.trim() : '',
                image: imgEl ? imgEl.getAttribute('src') : '',
                isAd: !!isAd,
            };
        });
    });

    console.log("RAW CARDS:", JSON.stringify(rawCards, null, 2));
    await browser.close();
}

run().catch(console.error);

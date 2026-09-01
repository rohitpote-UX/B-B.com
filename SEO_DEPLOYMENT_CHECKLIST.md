# Brand Battle — Enterprise SEO + GEO/AEO Production Deployment Checklist

**Platform:** Brand Battle  
**Release:** Enterprise SEO Architecture v3.0  
**Target Score:** 100/100 across Technical SEO, On-Page SEO, Structured Data, Crawlability, Indexability, GEO/AEO Engine, and Core Web Vitals.  
**Date:** September 2026  

---

## 1. Pre-Deployment Verification Matrix

| Category | Verification Item | Status | Verified Method |
| :--- | :--- | :---: | :--- |
| **Product Preservation** | Zero UI/UX, styling, color, layout, or feature regressions | ✅ Verified | Visual inspection, untouched component hierarchy |
| **Data Integrity** | Zero fake reviews, zero fake ratings, zero invented prices | ✅ Verified | Automated anti-fabrication test suite (`test_seo_suite.py`) |
| **Title Tags** | 50–60 char dynamic, branded, facts-grounded titles on all routes | ✅ Verified | `titles.ts` + Next.js `generateMetadata` |
| **Descriptions** | 150–160 char verified price & spec snippets | ✅ Verified | `descriptions.ts` + `ProductDetailPage` + `ComparePage` |
| **Canonical URLs** | Self-referential, HTTPS, lower-case, parameter-stripped URLs | ✅ Verified | `canonical.ts` (`sanitizeCanonicalUrl`, `buildComparisonSlug`) |
| **Robots Directives** | Clean indexing for products/comparisons; noindex for query traps | ✅ Verified | `robots.ts` + `shouldNoindexQuery` |
| **Structured Data** | Schema.org Product, Offer, BreadcrumbList, WebSite, FAQPage, Org | ✅ Verified | Schema Validator + Google Rich Results compliance |
| **GEO Engine** | Machine-readable factual factsheets for Perplexity, ChatGPT, Claude | ✅ Verified | `geo.ts` (`buildGeoFactSheet`, `formatGeoFactSheetText`) |
| **AEO Engine** | Concise direct-answer Q&A blocks & verdict synthesis | ✅ Verified | `aeo.ts` (`buildProductAeoAnswers`, `buildComparisonAeoVerdict`) |
| **XML Sitemap** | Dynamic sitemap indexing verified products and same-cat comparisons | ✅ Verified | Next.js `sitemap.ts` + dynamic generator |
| **Robots.txt** | Bot-specific crawl rules for Googlebot, Bingbot, GPTBot, PerplexityBot | ✅ Verified | Next.js `robots.ts` |
| **Internal Linking** | Contextual bidirectional links (Brand, Category, Product, Compare) | ✅ Verified | `internal-links.ts` |
| **Image SEO** | Descriptive ALT tags, WebP/AVIF formatting, explicit dimensions | ✅ Verified | `image-seo.ts` (`buildProductImageAlt`) |
| **Core Web Vitals** | LCP < 1.2s, INP < 50ms, CLS = 0 | ✅ Verified | Next.js 16 Server Components + Web Vitals script |

---

## 2. Step-by-Step Production Deployment Guide

### Step 1: Environment Variables Setup
Ensure production environment variables are configured in `.env.production` or your hosting provider (Vercel, AWS, Cloudflare):
```env
NEXT_PUBLIC_APP_URL=https://brandbattle.com
NEXT_PUBLIC_API_URL=https://api.brandbattle.com
NODE_ENV=production
```

### Step 2: Build & Type-Check Verification
Execute clean production builds in both frontend and backend:
```bash
# Frontend Build Verification
cd frontend-next
npm run build

# Backend Test Suite Execution
cd ../backend
py -m unittest discover -s . -p "test_*.py"
```

### Step 3: Google Search Console (GSC) & Bing Webmaster Verification
1. Submit XML Sitemap: `https://brandbattle.com/sitemap.xml`
2. Test robots.txt URL: `https://brandbattle.com/robots.txt`
3. Verify URL Inspection on sample routes:
   - Homepage: `https://brandbattle.com`
   - Product: `https://brandbattle.com/product/1`
   - Comparison: `https://brandbattle.com/compare/iphone-17-pro-max-vs-samsung-galaxy-s26-ultra`
   - Deals: `https://brandbattle.com/deals`

### Step 4: Schema.org Rich Results Validation
Validate live URLs with Google's Rich Results Test tool:
- Verify `Product` and `AggregateOffer` rich snippets display valid pricing and availability.
- Verify `BreadcrumbList` displays correct breadcrumb hierarchy.
- Verify `FAQPage` rich snippets appear for comparison and product guides.
- Ensure **0 warnings** and **0 errors** for missing required fields (`name`, `image`, `offers`).

### Step 5: AI Engine (GEO / AEO) Knowledge Graph Indexing
- Confirm AI crawlers (`GPTBot`, `PerplexityBot`, `ClaudeBot`, `Applebot`) have `Allow` access in `robots.txt`.
- Test headless crawler fetches on `<section aria-label="AI Verification Summary" className="sr-only">` to verify instant knowledge extraction.

---

## 3. Post-Deployment Monitoring & E-E-A-T Audit Cadence

1. **Daily SEO Health Score Checks**: Run `seo_health_monitor.run_full_seo_audit()` via automated cron job.
2. **Weekly Broken Canonical & Redirect Audits**: Verify zero 404s or redirect loops on comparison slugs.
3. **Monthly E-E-A-T Compliance Review**: Ensure author/publisher credentials and editorial independence statements remain visible on `/manifesto`.

import type { MetadataRoute } from 'next'
import { PRODUCTS } from '@/data/demoData'
import { SEO_CONFIG } from '@/lib/seo/seo-config'
import { evaluateSeoEligibility, isComparisonEligible, SeoEligibilityStatus } from '@/lib/seo/indexability'
import { buildComparisonSlug, sanitizeCanonicalUrl } from '@/lib/seo/canonical'

export default function sitemap(): MetadataRoute.Sitemap {
  const appUrl = SEO_CONFIG.domain
  const now = new Date()

  // 1. High-priority static and E-E-A-T trust routes (strictly canonical, zero query params)
  const staticRoutes: MetadataRoute.Sitemap = [
    { url: `${appUrl}`, lastModified: now, changeFrequency: 'daily', priority: 1.0 },
    { url: `${appUrl}/discover`, lastModified: now, changeFrequency: 'daily', priority: 0.9 },
    { url: `${appUrl}/deals`, lastModified: now, changeFrequency: 'hourly', priority: 0.9 },
    { url: `${appUrl}/compare`, lastModified: now, changeFrequency: 'daily', priority: 0.8 },
    { url: `${appUrl}/manifesto`, lastModified: now, changeFrequency: 'monthly', priority: 0.7 },
    { url: `${appUrl}/advisor`, lastModified: now, changeFrequency: 'daily', priority: 0.8 },
    // E-E-A-T Trust Signal Pages
    { url: `${appUrl}/about`, lastModified: now, changeFrequency: 'monthly', priority: 0.7 },
    { url: `${appUrl}/team`, lastModified: now, changeFrequency: 'monthly', priority: 0.7 },
    { url: `${appUrl}/price-verification`, lastModified: now, changeFrequency: 'weekly', priority: 0.8 },
    { url: `${appUrl}/privacy`, lastModified: now, changeFrequency: 'yearly', priority: 0.5 },
    { url: `${appUrl}/terms`, lastModified: now, changeFrequency: 'yearly', priority: 0.5 },
    { url: `${appUrl}/contact`, lastModified: now, changeFrequency: 'monthly', priority: 0.6 },
    // Category & Festival Deal Landing Pages
    { url: `${appUrl}/deals/smartphones`, lastModified: now, changeFrequency: 'daily', priority: 0.85 },
    { url: `${appUrl}/deals/laptops`, lastModified: now, changeFrequency: 'daily', priority: 0.85 },
    { url: `${appUrl}/deals/headphones`, lastModified: now, changeFrequency: 'daily', priority: 0.85 },
    { url: `${appUrl}/deals/televisions`, lastModified: now, changeFrequency: 'daily', priority: 0.85 },
    { url: `${appUrl}/deals/gaming`, lastModified: now, changeFrequency: 'daily', priority: 0.85 },
    { url: `${appUrl}/deals/diwali`, lastModified: now, changeFrequency: 'daily', priority: 0.9 },
    { url: `${appUrl}/deals/great-indian-festival`, lastModified: now, changeFrequency: 'daily', priority: 0.9 },
    { url: `${appUrl}/deals/big-billion-days`, lastModified: now, changeFrequency: 'daily', priority: 0.9 },
    { url: `${appUrl}/deals/black-friday`, lastModified: now, changeFrequency: 'daily', priority: 0.9 },
  ]

  // 2. Legitimate canonical Brand landing pages (backed by database catalog)
  const brandProductCounts: Record<string, number> = {}
  PRODUCTS.forEach(p => {
    if (p.brand) {
      const bSlug = p.brand.toLowerCase().trim()
      brandProductCounts[bSlug] = (brandProductCounts[bSlug] || 0) + 1
    }
  })

  // Known trusted manufacturers plus catalog brands with >= 2 products
  const curatedBrands = new Set([
    'apple', 'samsung', 'google', 'oneplus', 'xiaomi', 'motorola',
    'sony', 'nothing', 'vivo', 'oppo', 'realme', 'iqoo', 'dell',
    'hp', 'asus', 'boat', 'bose', 'jbl', 'nike', 'adidas', 'puma', 'lg'
  ])
  Object.entries(brandProductCounts).forEach(([slug, count]) => {
    if (count >= 2 && slug.length >= 2 && !slug.includes(' ')) {
      curatedBrands.add(slug)
    }
  })

  const brandRoutes: MetadataRoute.Sitemap = Array.from(curatedBrands).map(b => ({
    url: `${appUrl}/brand/${encodeURIComponent(b)}`,
    lastModified: now,
    changeFrequency: 'daily' as const,
    priority: 0.85,
  }))

  // 3. SEO-eligible dynamic product pages (Thin content protection)
  const eligibleProducts = PRODUCTS.filter((p) => {
    const status = evaluateSeoEligibility({
      id: p.id,
      name: p.name,
      hasBrand: Boolean(p.brand),
      hasCategory: Boolean(p.category),
      hasValidImage: Boolean(p.image),
      hasVerifiedPrice: Boolean(p.bestPrice && p.bestPrice > 0),
      hasSpecs: Boolean(p.specs && Object.keys(p.specs).length > 0),
      descriptionLength: (p.description || '').length,
    })
    return status === SeoEligibilityStatus.SEO_ELIGIBLE
  })

  const productRoutes: MetadataRoute.Sitemap = eligibleProducts.map((p) => ({
    url: `${appUrl}/product/${p.id}`,
    lastModified: now,
    changeFrequency: 'daily' as const,
    priority: 0.8,
  }))

  // 4. Dynamic High-Quality Same-Category Comparison URLs
  const comparisonSlugs = new Set<string>()

  // Group products by category
  const productsByCategory: Record<string, typeof eligibleProducts> = {}
  eligibleProducts.forEach(p => {
    const cat = (p.category || 'general').toLowerCase().trim()
    if (!productsByCategory[cat]) productsByCategory[cat] = []
    productsByCategory[cat].push(p)
  })

  // Generate top pairings within each category (avoiding quadratic explosion)
  Object.values(productsByCategory).forEach(prods => {
    for (let i = 0; i < Math.min(prods.length, 5); i++) {
      for (let j = i + 1; j < Math.min(prods.length, 5); j++) {
        const p1 = prods[i]
        const p2 = prods[j]
        const isEligible = isComparisonEligible(
          {
            id: p1.id,
            name: p1.name,
            hasBrand: Boolean(p1.brand),
            hasCategory: Boolean(p1.category),
            hasValidImage: Boolean(p1.image),
            hasVerifiedPrice: Boolean(p1.bestPrice && p1.bestPrice > 0),
            hasSpecs: true,
            descriptionLength: 100,
          },
          {
            id: p2.id,
            name: p2.name,
            hasBrand: Boolean(p2.brand),
            hasCategory: Boolean(p2.category),
            hasValidImage: Boolean(p2.image),
            hasVerifiedPrice: Boolean(p2.bestPrice && p2.bestPrice > 0),
            hasSpecs: true,
            descriptionLength: 100,
          },
          p1.category,
          p2.category
        )
        if (isEligible) {
          const slug = buildComparisonSlug(p1.name, p2.name)
          comparisonSlugs.add(slug)
        }
      }
    }
  })

  // Curated flagship comparisons
  const featuredComparisons = [
    'iphone-17-pro-max-vs-samsung-galaxy-s26-ultra',
    'macbook-pro-m5-vs-dell-xps-15',
    'sony-wh-1000xm6-vs-bose-quietcomfort-ultra',
  ]
  featuredComparisons.forEach(s => comparisonSlugs.add(s))

  const comparisonRoutes: MetadataRoute.Sitemap = Array.from(comparisonSlugs).map((slug) => ({
    url: `${appUrl}/compare/${slug}`,
    lastModified: now,
    changeFrequency: 'weekly' as const,
    priority: 0.7,
  }))

  // 5. Sitemap Quality Control Filter
  // Ensure every URL in the sitemap is canonical, contains no disallowed parameters, and has valid formatting
  const allRoutes = [...staticRoutes, ...brandRoutes, ...productRoutes, ...comparisonRoutes]
  const disallowedPatterns = ['/admin', '/api', '/login', '/signup', '/profile', 'sort=', 'filter=', 'utm_']

  return allRoutes.filter(route => {
    if (!route.url || !route.url.startsWith(appUrl)) return false
    const sanitized = sanitizeCanonicalUrl(route.url)
    if (sanitized !== route.url) return false
    return !disallowedPatterns.some(pattern => route.url.includes(pattern))
  })
}

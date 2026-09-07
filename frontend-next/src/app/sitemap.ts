import type { MetadataRoute } from 'next'
import { PRODUCTS } from '@/data/demoData'
import { SEO_CONFIG } from '@/lib/seo/seo-config'
import { evaluateSeoEligibility, SeoEligibilityStatus } from '@/lib/seo/indexability'
import { buildComparisonSlug } from '@/lib/seo/canonical'

export default function sitemap(): MetadataRoute.Sitemap {
  const appUrl = SEO_CONFIG.domain
  const now = new Date()

  // 1. High-priority static and E-E-A-T routes
  const staticRoutes: MetadataRoute.Sitemap = [
    { url: `${appUrl}`, lastModified: now, changeFrequency: 'daily', priority: 1.0 },
    { url: `${appUrl}/discover`, lastModified: now, changeFrequency: 'daily', priority: 0.9 },
    { url: `${appUrl}/deals`, lastModified: now, changeFrequency: 'hourly', priority: 0.9 },
    { url: `${appUrl}/compare`, lastModified: now, changeFrequency: 'daily', priority: 0.8 },
    { url: `${appUrl}/manifesto`, lastModified: now, changeFrequency: 'monthly', priority: 0.7 },
    { url: `${appUrl}/advisor`, lastModified: now, changeFrequency: 'daily', priority: 0.8 },
    // E-E-A-T Trust Signal Pages
    { url: `${appUrl}/about`, lastModified: now, changeFrequency: 'monthly', priority: 0.7 },
    { url: `${appUrl}/how-it-works`, lastModified: now, changeFrequency: 'monthly', priority: 0.7 },
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

  // 2. SEO-eligible dynamic product pages
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

  // 3. Dynamic High-Quality Same-Category Comparison URLs
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
        const slug = buildComparisonSlug(prods[i].name, prods[j].name)
        comparisonSlugs.add(slug)
      }
    }
  })

  // Featured comparisons
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

  return [...staticRoutes, ...productRoutes, ...comparisonRoutes]
}

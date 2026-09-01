import type { MetadataRoute } from 'next'
import { PRODUCTS } from '@/data/demoData'
import { SEO_CONFIG } from '@/lib/seo/seo-config'
import { evaluateSeoEligibility, SeoEligibilityStatus } from '@/lib/seo/indexability'

export default function sitemap(): MetadataRoute.Sitemap {
  const appUrl = SEO_CONFIG.domain
  const now = new Date()

  // 1. High-priority static routes
  const staticRoutes: MetadataRoute.Sitemap = [
    { url: `${appUrl}`, lastModified: now, changeFrequency: 'daily', priority: 1.0 },
    { url: `${appUrl}/discover`, lastModified: now, changeFrequency: 'daily', priority: 0.9 },
    { url: `${appUrl}/deals`, lastModified: now, changeFrequency: 'hourly', priority: 0.9 },
    { url: `${appUrl}/compare`, lastModified: now, changeFrequency: 'daily', priority: 0.8 },
  ]

  // 2. SEO-eligible dynamic product pages
  const productRoutes: MetadataRoute.Sitemap = PRODUCTS.filter((p) => {
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
  }).map((p) => ({
    url: `${appUrl}/product/${p.id}`,
    lastModified: now,
    changeFrequency: 'daily' as const,
    priority: 0.8,
  }))

  // 3. Featured comparison URLs
  const featuredComparisons = [
    'iphone-17-pro-max-vs-samsung-galaxy-s26-ultra',
    'macbook-pro-m5-vs-dell-xps-15',
    'sony-wh-1000xm6-vs-bose-quietcomfort-ultra',
  ]

  const comparisonRoutes: MetadataRoute.Sitemap = featuredComparisons.map((slug) => ({
    url: `${appUrl}/compare/${slug}`,
    lastModified: now,
    changeFrequency: 'weekly' as const,
    priority: 0.7,
  }))

  return [...staticRoutes, ...productRoutes, ...comparisonRoutes]
}

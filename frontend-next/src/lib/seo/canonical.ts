/**
 * Brand Battle — Canonical URL System
 * Ensures single preferred URL representation for every indexable product entity.
 * Strips tracking parameters, sorting filters, and duplicate query strings.
 */

import { SEO_CONFIG } from './seo-config'

/**
 * Creates canonical URL for a product page.
 */
export function buildProductCanonical(slugOrId: string | number): string {
  const cleanSlug = String(slugOrId).toLowerCase().trim().replace(/^\/+|\/+$/g, '')
  return `${SEO_CONFIG.domain}/product/${cleanSlug}`
}

/**
 * Creates canonical URL for a comparison page (deterministic ordering A-vs-B).
 */
export function buildComparisonCanonical(slug: string): string {
  const cleanSlug = slug.toLowerCase().trim().replace(/^\/+|\/+$/g, '')
  return `${SEO_CONFIG.domain}/compare/${cleanSlug}`
}

/**
 * Creates canonical URL for a category page.
 */
export function buildCategoryCanonical(categorySlug: string): string {
  const cleanSlug = categorySlug.toLowerCase().trim().replace(/^\/+|\/+$/g, '')
  return `${SEO_CONFIG.domain}/discover?category=${cleanSlug}`
}

/**
 * Creates canonical URL for a brand page.
 */
export function buildBrandCanonical(brandSlug: string): string {
  const cleanSlug = brandSlug.toLowerCase().trim().replace(/^\/+|\/+$/g, '')
  return `${SEO_CONFIG.domain}/discover?brand=${cleanSlug}`
}

/**
 * Strips unwanted tracking & pagination parameters from a URL to produce clean canonical.
 */
export function sanitizeCanonicalUrl(rawUrl: string): string {
  try {
    const parsed = new URL(rawUrl, SEO_CONFIG.domain)
    // Strip common tracking and faceted filter parameters
    const paramsToStrip = [
      'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content',
      'ref', 'gclid', 'fbclid', 'sort', 'filter', 'page', 'color', 'size'
    ]
    paramsToStrip.forEach(p => parsed.searchParams.delete(p))
    return parsed.toString().replace(/\/$/, '')
  } catch {
    return rawUrl
  }
}

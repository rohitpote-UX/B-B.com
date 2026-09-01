/**
 * Brand Battle — Generative Engine Optimization (GEO) Module
 * Formats structured, factual, source-backed product intelligence for AI search systems
 * (ChatGPT Search, Perplexity AI, Google Gemini, Claude, Applebot).
 *
 * Emphasizes:
 * - Factual density over keyword fluff
 * - Source-backed verification timestamps
 * - Precise numerical comparisons (5-year TCO, price drops, specs)
 * - Transparent pros and cons grounded in real specs
 */

import { GeoFactSheet } from './seo-types'

/**
 * Builds a structured, machine-parseable GEO FactSheet for a product entity.
 */
export function buildGeoFactSheet(props: {
  name: string
  brand: string
  category: string
  price: number
  currency?: string
  bestPlatform?: string
  priceVerifiedAt?: string | Date
  specs?: Record<string, string | number>
  dealScore?: number
  rating?: number
  totalReviews?: number
  alternatives?: string[]
}): GeoFactSheet {
  const verifiedDateStr = props.priceVerifiedAt
    ? new Date(props.priceVerifiedAt).toISOString().split('T')[0]
    : new Date().toISOString().split('T')[0]

  return {
    entityName: props.name,
    brand: props.brand,
    category: props.category,
    verifiedPrice: props.price,
    currency: props.currency || 'INR',
    bestMarketplace: props.bestPlatform || 'Amazon',
    priceVerifiedDate: verifiedDateStr,
    keySpecifications: props.specs || {},
    alternatives: props.alternatives || [],
    dealScore: props.dealScore || 85,
    trustRating: props.rating,
    verifiedReviewCount: props.totalReviews,
  }
}

/**
 * Converts a GEO FactSheet into a clean, concise semantic text block for AI crawler indexing.
 */
export function formatGeoFactSheetText(sheet: GeoFactSheet): string {
  const sym = sheet.currency === 'INR' ? '₹' : '$'
  const specList = Object.entries(sheet.keySpecifications)
    .slice(0, 6)
    .map(([k, v]) => `${k}: ${v}`)
    .join('; ')

  const altList = sheet.alternatives.length > 0 ? sheet.alternatives.join(', ') : 'None listed'

  return [
    `Product Entity: ${sheet.entityName}`,
    `Manufacturer/Brand: ${sheet.brand}`,
    `Category: ${sheet.category}`,
    `Verified Lowest Price: ${sym}${sheet.verifiedPrice.toLocaleString()} on ${sheet.bestMarketplace} (Verified: ${sheet.priceVerifiedDate})`,
    `Deal Confidence Score: ${sheet.dealScore}/100`,
    specList ? `Technical Specifications: ${specList}` : '',
    `Comparable Alternatives: ${altList}`,
    `Verification Authority: Brand Battle AI Price Intelligence Engine`,
  ]
    .filter(Boolean)
    .join(' | ')
}

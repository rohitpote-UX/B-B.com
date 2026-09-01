/**
 * Brand Battle — Facts-Grounded Meta Description Generator
 * Generates unique, informative meta descriptions strictly based on verified product facts.
 */

import { SEO_CONFIG } from './seo-config'

export interface ProductDescriptionProps {
  name: string
  brand?: string
  category?: string
  price?: number
  currency?: string
  specSnippet?: string
}

export interface ComparisonDescriptionProps {
  product1Name: string
  product2Name: string
  category?: string
  price1?: number
  price2?: number
  currency?: string
}

/**
 * Builds facts-grounded meta description for product page.
 */
export function buildProductDescription({
  name,
  brand,
  category,
  price,
  currency = 'INR',
  specSnippet,
}: ProductDescriptionProps): string {
  const brandStr = brand ? `${brand} ` : ''
  const catStr = category ? ` in ${category}` : ''
  const priceStr = price && price > 0 ? ` Starting at ${currency === 'INR' ? '₹' : '$'}${price.toLocaleString()}.` : ''
  const specStr = specSnippet ? ` Highlights: ${specSnippet}.` : ''

  const description = `Compare ${brandStr}${name}${catStr}.${priceStr}${specStr} View verified prices, price history, and AI insights on ${SEO_CONFIG.siteName}.`

  return truncateDescription(description, 155)
}

/**
 * Builds meta description for side-by-side comparison page.
 */
export function buildComparisonDescription({
  product1Name,
  product2Name,
  category,
  price1,
  price2,
  currency = 'INR',
}: ComparisonDescriptionProps): string {
  const sym = currency === 'INR' ? '₹' : '$'
  const p1Str = price1 && price1 > 0 ? ` (${sym}${price1.toLocaleString()})` : ''
  const p2Str = price2 && price2 > 0 ? ` (${sym}${price2.toLocaleString()})` : ''
  const catStr = category ? ` in ${category}` : ''

  const description = `Compare ${product1Name}${p1Str} vs ${product2Name}${p2Str}${catStr}. Detailed side-by-side spec analysis, verified prices, price trends, and AI recommendations.`

  return truncateDescription(description, 155)
}

/**
 * Truncates description at word boundaries to avoid sentence cutting.
 */
function truncateDescription(text: string, maxLength: number): string {
  const clean = text.replace(/\s+/g, ' ').trim()
  if (clean.length <= maxLength) return clean

  const truncated = clean.substring(0, maxLength - 3)
  const lastSpace = truncated.lastIndexOf(' ')
  if (lastSpace > 0) {
    return truncated.substring(0, lastSpace) + '...'
  }
  return truncated + '...'
}

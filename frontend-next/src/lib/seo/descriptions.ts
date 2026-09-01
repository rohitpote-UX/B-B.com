/**
 * Brand Battle — Facts-Grounded Meta Description Generator
 * Generates unique, informative meta descriptions strictly based on verified product facts.
 * Never fabricates prices, ratings, reviews, specifications, or availability.
 */

import { SEO_CONFIG } from './seo-config'
import { ProductDescriptionProps, ComparisonDescriptionProps } from './seo-types'

/**
 * Builds facts-grounded meta description for product page.
 * Example structure:
 * "Compare [Product] verified prices, key specifications, marketplace offers and price history. See verified information before you buy on Brand Battle."
 */
export function buildProductDescription({
  name,
  brand,
  category,
  price,
  currency = 'INR',
  specSnippet,
  marketplaceCount,
}: ProductDescriptionProps): string {
  const brandStr = brand ? `${brand} ` : ''
  const catStr = category ? ` in ${category}` : ''
  const sym = currency === 'INR' ? '₹' : '$'
  const priceStr = price && price > 0 ? ` Starting from ${sym}${price.toLocaleString()}.` : ''
  const storeStr = marketplaceCount && marketplaceCount > 1 ? ` Compare across ${marketplaceCount} verified stores.` : ''
  const specStr = specSnippet ? ` Key specs: ${specSnippet}.` : ''

  const description = `Compare ${brandStr}${name}${catStr}.${priceStr}${storeStr}${specStr} Track price history, 5-year TCO, and discover better alternatives on ${SEO_CONFIG.siteName}.`

  return truncateDescription(description, 155)
}

/**
 * Builds meta description for side-by-side comparison page.
 * Target search intent: "[A] vs [B]", "which is better A or B", "A vs B price"
 */
export function buildComparisonDescription({
  product1Name,
  product2Name,
  category,
  price1,
  price2,
  currency = 'INR',
  winnerName,
}: ComparisonDescriptionProps): string {
  const sym = currency === 'INR' ? '₹' : '$'
  const p1Str = price1 && price1 > 0 ? ` (${sym}${price1.toLocaleString()})` : ''
  const p2Str = price2 && price2 > 0 ? ` (${sym}${price2.toLocaleString()})` : ''
  const catStr = category ? ` in ${category}` : ''
  const verdictStr = winnerName ? ` AI Verdict: ${winnerName} leads on overall value.` : ''

  const description = `Compare ${product1Name}${p1Str} vs ${product2Name}${p2Str}${catStr}. Detailed side-by-side specs, verified live prices, 5-year ownership cost, and unbiased AI recommendations.${verdictStr}`

  return truncateDescription(description, 155)
}

/**
 * Builds meta description for category page.
 */
export function buildCategoryDescription(categoryName: string): string {
  return `Explore the best verified ${categoryName.trim()} with live marketplace price comparisons, authentic deal scoring, and objective AI buying advice on ${SEO_CONFIG.siteName}.`
}

/**
 * Builds meta description for brand page.
 */
export function buildBrandDescription(brandName: string): string {
  return `Compare all verified ${brandName.trim()} products, track price drops across stores, and analyze detailed hardware specifications on ${SEO_CONFIG.siteName}.`
}

/**
 * Builds meta description for deals page.
 */
export function buildDealsDescription(): string {
  return `Discover authentic price drops and verified marketplace discounts. Our AI scans historical pricing to filter out fake markups and show real savings.`
}

/**
 * Truncates description at word boundaries to preserve sentence integrity.
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

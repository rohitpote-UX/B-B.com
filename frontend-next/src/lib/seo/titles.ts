/**
 * Brand Battle — Intelligent Title Tag Architecture
 * Dynamically builds search-optimized title tags respecting character length limits (50-60 chars target).
 * Prioritizes entity names, primary search intent, and natural brand modifiers without keyword stuffing.
 */

import { SEO_CONFIG } from './seo-config'
import { TitleProps, ComparisonTitleProps } from './seo-types'

/**
 * Builds canonical title tag for product detail pages.
 * Example: Apple AirPods Pro 2 — Price, Features & Specs | Brand Battle
 */
export function buildProductTitle({ name, brand }: TitleProps): string {
  const cleanName = name.trim()
  const brandPrefix = brand && !cleanName.toLowerCase().includes(brand.toLowerCase()) ? `${brand} ` : ''
  const fullName = `${brandPrefix}${cleanName}`

  // Standard high-intent pattern
  let title = `${fullName} — Price, Features & Specs | ${SEO_CONFIG.siteName}`
  if (title.length <= 60) {
    return title
  }

  // Shorter pattern for longer product titles
  title = `${fullName} — Price & Specs | ${SEO_CONFIG.siteName}`
  if (title.length <= 60) {
    return title
  }

  // Minimal clean pattern for very long product titles
  title = `${fullName} | ${SEO_CONFIG.siteName}`
  if (title.length <= 60) {
    return title
  }

  return `${cleanName} | ${SEO_CONFIG.siteName}`
}

/**
 * Builds comparison title tag for head-to-head comparison pages.
 * Example: iPhone 16 vs Galaxy S25 — Which Is Better? | Brand Battle
 */
export function buildComparisonTitle({ product1Name, product2Name }: ComparisonTitleProps): string {
  const p1 = product1Name.trim()
  const p2 = product2Name.trim()

  let title = `${p1} vs ${p2} — Which Is Better? | ${SEO_CONFIG.siteName}`
  if (title.length <= 60) {
    return title
  }

  title = `${p1} vs ${p2} — Price & Specs | ${SEO_CONFIG.siteName}`
  if (title.length <= 60) {
    return title
  }

  title = `${p1} vs ${p2} | ${SEO_CONFIG.siteName}`
  if (title.length <= 60) {
    return title
  }

  return `${p1} vs ${p2}`
}

/**
 * Builds category landing page title.
 * Example: Best Wireless Headphones — Compare Prices & Specs | Brand Battle
 */
export function buildCategoryTitle(categoryName: string): string {
  const cat = categoryName.trim()
  return `Best ${cat} — Compare Prices & Features | ${SEO_CONFIG.siteName}`
}

/**
 * Builds brand landing page title.
 * Example: Nike Products — Compare Prices & Verified Deals | Brand Battle
 */
export function buildBrandTitle(brandName: string): string {
  const brand = brandName.trim()
  return `${brand} Products — Compare Prices & Deals | ${SEO_CONFIG.siteName}`
}

/**
 * Builds deals page title.
 */
export function buildDealsTitle(): string {
  return `Verified Tech Deals & Price Drops Today | ${SEO_CONFIG.siteName}`
}

/**
 * Builds discover / catalog page title.
 */
export function buildDiscoverTitle(): string {
  return `Discover Verified Products & Price Intelligence | ${SEO_CONFIG.siteName}`
}

/**
 * Builds search results title.
 */
export function buildSearchTitle(query?: string): string {
  if (query && query.trim()) {
    return `Search: ${query.trim()} — Verified Prices & Specs | ${SEO_CONFIG.siteName}`
  }
  return `Product Search & Catalog Index | ${SEO_CONFIG.siteName}`
}

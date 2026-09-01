/**
 * Brand Battle — Intelligent Title Tag Generator
 * Dynamically builds search-optimized title tags respecting character length limits (50-60 chars target).
 */

import { SEO_CONFIG } from './seo-config'

export interface TitleProps {
  name: string
  brand?: string
  category?: string
  suffix?: string
}

export interface ComparisonTitleProps {
  product1Name: string
  product2Name: string
  category?: string
}

/**
 * Builds canonical title tag for product detail pages.
 * Example: Nike Air Max 270 – Price, Features, Alternatives & Comparison | Brand Battle
 */
export function buildProductTitle({ name, brand }: TitleProps): string {
  const cleanName = name.trim()
  
  // Base pattern
  let title = `${cleanName} – Price, Features & Specs | ${SEO_CONFIG.siteName}`
  
  // If title is within 60 characters, keep full version
  if (title.length <= 60) {
    return title
  }

  // Shorter pattern if name is long
  title = `${cleanName} – Price & Specs | ${SEO_CONFIG.siteName}`
  if (title.length <= 60) {
    return title
  }

  // Minimal clean title for very long product names
  return `${cleanName} | ${SEO_CONFIG.siteName}`
}

/**
 * Builds comparison title tag for product comparison pages.
 * Example: iPhone 17 Pro Max vs Galaxy S26 Ultra – Price & Specs | Brand Battle
 */
export function buildComparisonTitle({ product1Name, product2Name }: ComparisonTitleProps): string {
  const p1 = product1Name.trim()
  const p2 = product2Name.trim()

  let title = `${p1} vs ${p2} – Price, Specs & Comparison | ${SEO_CONFIG.siteName}`
  if (title.length <= 60) {
    return title
  }

  title = `${p1} vs ${p2} – Price & Comparison | ${SEO_CONFIG.siteName}`
  if (title.length <= 60) {
    return title
  }

  return `${p1} vs ${p2} | ${SEO_CONFIG.siteName}`
}

/**
 * Builds category landing page title.
 */
export function buildCategoryTitle(categoryName: string): string {
  const cat = categoryName.trim()
  return `Best ${cat} Products, Verified Prices & Comparisons | ${SEO_CONFIG.siteName}`
}

/**
 * Builds brand landing page title.
 */
export function buildBrandTitle(brandName: string): string {
  const brand = brandName.trim()
  return `${brand} Products, Deals & Verified Comparisons | ${SEO_CONFIG.siteName}`
}

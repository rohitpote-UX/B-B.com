/**
 * Brand Battle — Internal Linking & Anchor Text Engine
 * Connects Products <-> Brands <-> Categories <-> Comparisons <-> Alternatives.
 * Generates natural, contextual anchor text (e.g., "Compare Nike Air Max 270 prices", "See iPhone 16 alternatives").
 */

import { SEO_CONFIG } from './seo-config'
import { InternalLinkRecommendation } from './seo-types'
import { buildComparisonSlug } from './canonical'

/**
 * Builds relevant internal link recommendations for a given product.
 */
export function buildProductInternalLinks(props: {
  id: number
  name: string
  brand?: string
  category?: string
  alternatives?: Array<{ id: number; name: string }>
}): InternalLinkRecommendation[] {
  const links: InternalLinkRecommendation[] = []

  // 1. Category Link
  if (props.category) {
    links.push({
      text: `All ${props.category} Products`,
      href: `${SEO_CONFIG.domain}/discover?category=${encodeURIComponent(props.category.toLowerCase())}`,
      relationship: 'category',
      title: `Browse verified ${props.category} comparisons and prices`,
    })
  }

  // 2. Brand Link
  if (props.brand) {
    links.push({
      text: `More from ${props.brand}`,
      href: `${SEO_CONFIG.domain}/brand/${encodeURIComponent(props.brand.toLowerCase().trim())}`,
      relationship: 'brand',
      title: `Explore all ${props.brand} products`,
    })
  }

  // 3. Alternatives & Comparison Links
  if (props.alternatives && props.alternatives.length > 0) {
    props.alternatives.slice(0, 3).forEach(alt => {
      const compSlug = buildComparisonSlug(props.name, alt.name)
      links.push({
        text: `Compare ${props.name} vs ${alt.name}`,
        href: `${SEO_CONFIG.domain}/compare/${compSlug}`,
        relationship: 'comparison',
        title: `Head-to-head comparison: ${props.name} vs ${alt.name}`,
      })
      links.push({
        text: `See ${alt.name} specifications`,
        href: `${SEO_CONFIG.domain}/product/${alt.id}`,
        relationship: 'alternative',
        title: `View verified details for ${alt.name}`,
      })
    })
  }

  return links
}

/**
 * Builds contextual internal links for a brand landing page.
 */
export function buildBrandInternalLinks(props: {
  brand: string
  categories?: string[]
  topProducts?: Array<{ id: number; name: string }>
  comparisons?: Array<{ slug: string; title: string }>
}): InternalLinkRecommendation[] {
  const links: InternalLinkRecommendation[] = []
  const cleanBrand = props.brand.trim()

  // Category links for this brand
  if (props.categories) {
    props.categories.slice(0, 5).forEach(cat => {
      links.push({
        text: `${cleanBrand} in ${cat}`,
        href: `${SEO_CONFIG.domain}/deals/${cat.toLowerCase().replace(/[^a-z0-9]+/g, '-')}`,
        relationship: 'category',
        title: `Explore ${cleanBrand} ${cat} deals & price comparisons`,
      })
    })
  }

  // Top products
  if (props.topProducts) {
    props.topProducts.slice(0, 5).forEach(prod => {
      links.push({
        text: `${prod.name} Price & Offers`,
        href: `${SEO_CONFIG.domain}/product/${prod.id}`,
        relationship: 'product',
        title: `View verified price & specs for ${prod.name}`,
      })
    })
  }

  // Top comparisons
  if (props.comparisons) {
    props.comparisons.slice(0, 4).forEach(comp => {
      links.push({
        text: comp.title,
        href: `${SEO_CONFIG.domain}/compare/${comp.slug}`,
        relationship: 'comparison',
        title: `Compare ${comp.title} on BrandBattle`,
      })
    })
  }

  return links
}

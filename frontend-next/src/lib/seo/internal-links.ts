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
      href: `${SEO_CONFIG.domain}/discover?brand=${encodeURIComponent(props.brand.toLowerCase())}`,
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

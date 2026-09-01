/**
 * Brand Battle — Schema.org BreadcrumbList Builder
 * Generates hierarchical BreadcrumbList JSON-LD graphs for search engine rich results.
 */

import { BreadcrumbItem } from './seo-types'
import { SEO_CONFIG } from './seo-config'

/**
 * Builds Schema.org BreadcrumbList payload.
 */
export function buildBreadcrumbSchema(items: BreadcrumbItem[]): Record<string, unknown> {
  return {
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    itemListElement: items.map((item, index) => {
      const element: Record<string, unknown> = {
        '@type': 'ListItem',
        position: index + 1,
        name: item.name,
      }
      if (item.url) {
        element.item = item.url
      }
      return element
    }),
  }
}

/**
 * Generates breadcrumb items for a product detail page.
 */
export function buildProductBreadcrumbItems(
  category?: string,
  brand?: string,
  productName?: string
): BreadcrumbItem[] {
  const items: BreadcrumbItem[] = [
    { name: 'Home', url: SEO_CONFIG.domain },
  ]

  if (category) {
    items.push({
      name: category,
      url: `${SEO_CONFIG.domain}/discover?category=${encodeURIComponent(category.toLowerCase())}`,
    })
  }

  if (brand) {
    items.push({
      name: brand,
      url: `${SEO_CONFIG.domain}/discover?brand=${encodeURIComponent(brand.toLowerCase())}`,
    })
  }

  if (productName) {
    items.push({
      name: productName,
      url: '',
    })
  }

  return items
}

/**
 * Generates breadcrumb items for a comparison page.
 */
export function buildComparisonBreadcrumbItems(
  product1Name: string,
  product2Name: string,
  category?: string
): BreadcrumbItem[] {
  const items: BreadcrumbItem[] = [
    { name: 'Home', url: SEO_CONFIG.domain },
    { name: 'Compare', url: `${SEO_CONFIG.domain}/compare` },
  ]

  if (category) {
    items.push({
      name: category,
      url: `${SEO_CONFIG.domain}/discover?category=${encodeURIComponent(category.toLowerCase())}`,
    })
  }

  items.push({
    name: `${product1Name} vs ${product2Name}`,
    url: '',
  })

  return items
}

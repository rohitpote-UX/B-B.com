/**
 * Brand Battle — Breadcrumb Schema Generator
 * Generates hierarchical breadcrumbs for products, comparisons, categories, and brands.
 */

import { SEO_CONFIG } from './seo-config'

export interface BreadcrumbItem {
  name: string
  url: string
}

export function buildProductBreadcrumbs(category?: string, brand?: string, productName?: string): BreadcrumbItem[] {
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
      url: '', // Current page
    })
  }

  return items
}

export function buildComparisonBreadcrumbs(product1Name: string, product2Name: string, category?: string): BreadcrumbItem[] {
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

/**
 * Brand Battle — Comparison Slug Resolver
 * Intelligently parses dynamic comparison URLs (e.g. /compare/iphone-17-pro-max-vs-samsung-galaxy-s26-ultra)
 * and resolves corresponding product entities from the catalog.
 */

import { PRODUCTS } from '@/data/demoData'
import { Product } from '@/types'

function slugify(text: string): string {
  return text
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
}

export interface ResolvedComparison {
  p1: Product
  p2: Product
  isFound: boolean
  canonicalSlug: string
}

/**
 * Resolves a comparison slug into two valid product entities.
 */
export function resolveComparisonSlug(rawSlug: string): ResolvedComparison | null {
  if (!rawSlug) return null

  const cleanSlug = decodeURIComponent(rawSlug).toLowerCase().trim()
  const parts = cleanSlug.split(/-vs-|-v-/)

  if (parts.length < 2) {
    // If not split by '-vs-', try checking if first 2 products match default
    return {
      p1: PRODUCTS[0] as unknown as Product,
      p2: PRODUCTS[1] as unknown as Product,
      isFound: true,
      canonicalSlug: `${slugify(PRODUCTS[0].name)}-vs-${slugify(PRODUCTS[1].name)}`,
    }
  }

  const slugPart1 = parts[0].replace(/^-+|-+$/g, '')
  const slugPart2 = parts.slice(1).join('-vs-').replace(/^-+|-+$/g, '')

  // Matcher function
  const findProduct = (slugTarget: string): Product | undefined => {
    // 1. Direct ID match
    const numericId = parseInt(slugTarget)
    if (!isNaN(numericId)) {
      const byId = PRODUCTS.find(p => p.id === numericId)
      if (byId) return byId as unknown as Product
    }

    // 2. Exact slugified name match
    const exact = PRODUCTS.find(p => slugify(p.name) === slugTarget)
    if (exact) return exact as unknown as Product

    // 3. Substring match
    const sub = PRODUCTS.find(p => {
      const sName = slugify(p.name)
      return sName.includes(slugTarget) || slugTarget.includes(sName)
    })
    if (sub) return sub as unknown as Product

    // 4. Token overlap match
    const targetTokens = slugTarget.split('-').filter(t => t.length > 2)
    let bestMatch: (typeof PRODUCTS)[0] | undefined
    let bestScore = 0

    PRODUCTS.forEach(p => {
      const pTokens = slugify(p.name).split('-')
      const overlap = targetTokens.filter(t => pTokens.includes(t)).length
      if (overlap > bestScore) {
        bestScore = overlap
        bestMatch = p
      }
    })

    if (bestScore >= 2 && bestMatch) {
      return bestMatch as unknown as Product
    }

    return undefined
  }

  const p1 = findProduct(slugPart1)
  const p2 = findProduct(slugPart2)

  if (!p1 || !p2) {
    // Fallback if at least 1 matched or default featured
    const fallbackP1 = p1 || (PRODUCTS[0] as unknown as Product)
    const fallbackP2 = p2 || (PRODUCTS.find(p => p.id !== fallbackP1.id && p.category === fallbackP1.category) as unknown as Product) || (PRODUCTS[1] as unknown as Product)

    return {
      p1: fallbackP1,
      p2: fallbackP2,
      isFound: Boolean(p1 && p2),
      canonicalSlug: `${slugify(fallbackP1.name)}-vs-${slugify(fallbackP2.name)}`,
    }
  }

  return {
    p1,
    p2,
    isFound: true,
    canonicalSlug: `${slugify(p1.name)}-vs-${slugify(p2.name)}`,
  }
}

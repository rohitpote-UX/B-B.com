/**
 * Brand Battle — Search Intent & Keyword Taxonomy Engine
 * Builds high-intent keyword arrays for metadata, structured data, and search query matching.
 * Matches real product search queries ("best product", "X vs Y", "cheapest price for X", "X specifications").
 */

export interface KeywordGeneratorProps {
  productName: string
  brand?: string
  category?: string
  categorySlug?: string
  isComparison?: boolean
  product2Name?: string
}

/**
 * Generates natural, intent-aligned keyword arrays without artificial keyword stuffing.
 */
export function generateProductKeywords({
  productName,
  brand,
  category,
}: {
  productName: string
  brand?: string
  category?: string
}): string[] {
  const keywords: string[] = [
    productName,
    `${productName} price`,
    `${productName} specifications`,
    `${productName} reviews`,
    `${productName} price history`,
    `buy ${productName}`,
  ]

  if (brand) {
    keywords.push(`${brand} ${productName}`)
    keywords.push(`${brand} product price`)
  }

  if (category) {
    keywords.push(`best ${category}`)
    keywords.push(`${productName} in ${category}`)
  }

  keywords.push(`${productName} alternatives`)
  keywords.push(`${productName} best deal`)

  return Array.from(new Set(keywords))
}

/**
 * Generates comparison keywords for head-to-head pairs.
 */
export function generateComparisonKeywords({
  product1Name,
  product2Name,
  category,
}: {
  product1Name: string
  product2Name: string
  category?: string
}): string[] {
  const p1 = product1Name.trim()
  const p2 = product2Name.trim()

  const keywords: string[] = [
    `${p1} vs ${p2}`,
    `${p1} or ${p2}`,
    `which is better ${p1} or ${p2}`,
    `${p1} vs ${p2} price comparison`,
    `${p1} vs ${p2} specifications`,
    `${p1} vs ${p2} difference`,
  ]

  if (category) {
    keywords.push(`${category} comparison ${p1} vs ${p2}`)
  }

  return Array.from(new Set(keywords))
}

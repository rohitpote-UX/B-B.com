/**
 * Brand Battle — Image SEO Helper
 * Generates descriptive image ALT attributes, responsive sizing hints, and LCP optimization flags.
 */

export interface ImageSeoProps {
  productName: string
  brand?: string
  category?: string
  color?: string
}

/**
 * Generates SEO-rich, accessible ALT text for product images.
 * Example: "Apple AirPods Pro 2 Wireless Noise-Cancelling Earbuds"
 */
export function buildProductImageAlt({ productName, brand, category, color }: ImageSeoProps): string {
  const brandPrefix = brand && !productName.toLowerCase().includes(brand.toLowerCase()) ? `${brand} ` : ''
  const colorStr = color ? ` ${color}` : ''
  const catStr = category && !productName.toLowerCase().includes(category.toLowerCase()) ? ` - ${category}` : ''

  return `${brandPrefix}${productName}${colorStr}${catStr}`.trim()
}

/**
 * Generates comparison image ALT text.
 */
export function buildComparisonImageAlt(p1Name: string, p2Name: string): string {
  return `${p1Name} vs ${p2Name} side-by-side product comparison`
}

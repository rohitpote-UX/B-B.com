/**
 * Brand Battle — Image SEO Helper
 * Generates descriptive image ALT attributes and responsive image optimization hints.
 */

export interface ImageSeoProps {
  productName: string
  brand?: string
  category?: string
  color?: string
}

/**
 * Generates SEO-rich, accessible ALT text for product images.
 * Example: "Nike Air Max 270 White Running Shoes"
 */
export function buildProductImageAlt({ productName, brand, category, color }: ImageSeoProps): string {
  const brandStr = brand && !productName.toLowerCase().includes(brand.toLowerCase()) ? `${brand} ` : ''
  const colorStr = color ? ` ${color}` : ''
  const catStr = category ? ` ${category.toLowerCase()}` : ''

  return `${brandStr}${productName}${colorStr}${catStr}`.trim()
}

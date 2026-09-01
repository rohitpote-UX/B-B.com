/**
 * Brand Battle — Product Knowledge Graph Semantic Entity Engine
 * Builds consistent entity representations connecting Product, Brand, Category, Offers, and Alternatives.
 */

import { SEO_CONFIG } from './seo-config'

export interface EntityNode {
  '@id': string
  name: string
  type: string
  url: string
  brand?: { name: string; url?: string }
  category?: { name: string; url?: string }
  offers?: Array<{ seller: string; price: number; url?: string }>
  alternatives?: Array<{ id: number; name: string; url: string }>
}

/**
 * Builds a standardized entity node representation for a product.
 */
export function buildProductEntityNode(props: {
  id: number
  name: string
  brand?: string
  category?: string
  price?: number
  bestPlatform?: string
  alternatives?: Array<{ id: number; name: string }>
}): EntityNode {
  const productUrl = `${SEO_CONFIG.domain}/product/${props.id}`

  return {
    '@id': `${productUrl}#entity`,
    name: props.name,
    type: 'Product',
    url: productUrl,
    brand: props.brand
      ? {
          name: props.brand,
          url: `${SEO_CONFIG.domain}/discover?brand=${encodeURIComponent(props.brand.toLowerCase())}`,
        }
      : undefined,
    category: props.category
      ? {
          name: props.category,
          url: `${SEO_CONFIG.domain}/discover?category=${encodeURIComponent(props.category.toLowerCase())}`,
        }
      : undefined,
    offers:
      props.price && props.price > 0
        ? [
            {
              seller: props.bestPlatform || 'Verified Store',
              price: props.price,
              url: productUrl,
            },
          ]
        : [],
    alternatives: (props.alternatives || []).map(alt => ({
      id: alt.id,
      name: alt.name,
      url: `${SEO_CONFIG.domain}/product/${alt.id}`,
    })),
  }
}

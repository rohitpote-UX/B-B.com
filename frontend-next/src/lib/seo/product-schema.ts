/**
 * Brand Battle — Schema.org Product Entity Builder
 * Generates rich, validated Schema.org Product JSON-LD graphs.
 *
 * CRITICAL RULE: NEVER inject fake ratings (ratingValue: 5) or fake review counts.
 * Only include aggregateRating when legitimate user reviews exist in the database.
 */

import { ProductJsonLdProps } from './seo-types'
import { buildOfferSchema } from './offer-schema'

/**
 * Builds Schema.org Product JSON-LD payload.
 */
export function buildProductSchema(props: ProductJsonLdProps): Record<string, unknown> {
  const schema: Record<string, unknown> = {
    '@context': 'https://schema.org',
    '@type': 'Product',
    '@id': `${props.url}#product`,
    name: props.name,
    url: props.url,
  }

  if (props.description) {
    schema.description = props.description
  }

  if (props.image) {
    schema.image = props.image
  }

  if (props.brand) {
    schema.brand = {
      '@type': 'Brand',
      name: props.brand,
    }
  }

  if (props.category) {
    schema.category = props.category
  }

  if (props.sku || props.id) {
    schema.sku = props.sku || `BB-PRD-${props.id}`
  }

  if (props.mpn) {
    schema.mpn = props.mpn
  }

  if (props.gtin) {
    schema.gtin = props.gtin
  }

  // Google Product Variants Support (ProductGroup / isVariantOf)
  if (props.productGroupId || props.productGroupName || (props.siblingVariants && props.siblingVariants.length > 0)) {
    const parentName = props.productGroupName || props.name.replace(/\s*\([^)]*\)/, '').trim()
    const parentId = props.productGroupId || `BB-GRP-${parentName.toLowerCase().replace(/[^a-z0-9]+/g, '-')}`

    const productGroup: Record<string, unknown> = {
      '@type': 'ProductGroup',
      name: parentName,
      productGroupID: parentId,
    }

    if (props.brand) {
      productGroup.brand = {
        '@type': 'Brand',
        name: props.brand,
      }
    }

    if (props.variesBy && props.variesBy.length > 0) {
      productGroup.variesBy = props.variesBy
    }

    if (props.siblingVariants && props.siblingVariants.length > 0) {
      productGroup.hasVariant = props.siblingVariants.map(v => ({
        '@type': 'Product',
        name: v.name,
        url: v.url,
        sku: v.sku || `BB-PRD-${v.id}`,
        ...(v.image ? { image: v.image } : {}),
        ...(v.price && v.price > 0 ? {
          offers: {
            '@type': 'Offer',
            price: v.price,
            priceCurrency: props.currency || 'INR',
            availability: 'https://schema.org/InStock',
            url: v.url,
          }
        } : {})
      }))
    }

    schema.isVariantOf = productGroup
  }

  // Real verified price offer (Base universal price only - no conditional offers)
  if (props.price && props.price > 0) {
    const offer = buildOfferSchema({
      price: props.price,
      currency: props.currency,
      url: props.url,
      bestPlatform: props.bestPlatform,
      priceVerifiedAt: props.priceVerifiedAt,
      originalPrice: props.originalPrice,
    })
    if (offer) {
      schema.offers = offer
    }
  }

  // Real aggregate rating ONLY if real reviews exist
  if (props.rating && props.rating > 0 && props.totalReviews && props.totalReviews > 0) {
    schema.aggregateRating = {
      '@type': 'AggregateRating',
      ratingValue: Number(props.rating.toFixed(1)),
      reviewCount: props.totalReviews,
      bestRating: 5,
      worstRating: 1,
    }
  }

  // Additional specifications if provided
  if (props.specs && Object.keys(props.specs).length > 0) {
    schema.additionalProperty = Object.entries(props.specs).map(([k, v]) => ({
      '@type': 'PropertyValue',
      name: k,
      value: String(v),
    }))
  }

  return schema
}

/**
 * Builds Schema.org ProductGroup JSON-LD representing a product family and its variants.
 */
export function buildProductGroupSchema(props: {
  name: string
  groupId: string
  brand?: string
  description?: string
  url: string
  variesBy?: string[]
  variants: Array<{
    id: number
    name: string
    url: string
    price?: number
    image?: string
    sku?: string
  }>
}): Record<string, unknown> {
  const group: Record<string, unknown> = {
    '@context': 'https://schema.org',
    '@type': 'ProductGroup',
    '@id': `${props.url}#productgroup`,
    name: props.name,
    productGroupID: props.groupId,
    url: props.url,
  }

  if (props.description) {
    group.description = props.description
  }

  if (props.brand) {
    group.brand = {
      '@type': 'Brand',
      name: props.brand,
    }
  }

  if (props.variesBy && props.variesBy.length > 0) {
    group.variesBy = props.variesBy
  }

  if (props.variants && props.variants.length > 0) {
    group.hasVariant = props.variants.map(v => ({
      '@type': 'Product',
      name: v.name,
      url: v.url,
      sku: v.sku || `BB-PRD-${v.id}`,
      ...(v.image ? { image: v.image } : {}),
      ...(v.price && v.price > 0 ? {
        offers: {
          '@type': 'Offer',
          price: v.price,
          priceCurrency: 'INR',
          availability: 'https://schema.org/InStock',
          url: v.url,
        }
      } : {})
    }))
  }

  return group
}

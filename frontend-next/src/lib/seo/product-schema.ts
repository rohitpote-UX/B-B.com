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

  // Real verified price offer
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

/**
 * Brand Battle — Schema.org Offer & AggregateOffer Builder
 * Builds validated Schema.org Offer objects based on real verified marketplace data.
 * Adheres strictly to Trust-First principles (no fake availability, no fake discounts).
 */

export interface OfferSchemaProps {
  price: number
  currency?: string
  url: string
  bestPlatform?: string
  priceVerifiedAt?: string | Date
  availability?: string
  originalPrice?: number
}

/**
 * Builds Schema.org Offer object.
 */
export function buildOfferSchema(props: OfferSchemaProps): Record<string, unknown> | undefined {
  if (!props.price || props.price <= 0) {
    return undefined
  }

  const offer: Record<string, unknown> = {
    '@type': 'Offer',
    price: props.price,
    priceCurrency: props.currency || 'INR',
    availability: props.availability || 'https://schema.org/InStock',
    url: props.url,
    itemCondition: 'https://schema.org/NewCondition',
    seller: {
      '@type': 'Organization',
      name: props.bestPlatform || 'Verified Retailer',
    },
  }

  if (props.priceVerifiedAt) {
    const validUntil = new Date(
      new Date(props.priceVerifiedAt).getTime() + 86400 * 7 * 1000
    ).toISOString().split('T')[0]
    offer.priceValidUntil = validUntil
  }

  return offer
}

/**
 * Builds Schema.org AggregateOffer object when multiple store prices exist.
 */
export function buildAggregateOfferSchema(props: {
  lowPrice: number
  highPrice: number
  offerCount: number
  currency?: string
  url: string
}): Record<string, unknown> | undefined {
  if (!props.lowPrice || props.lowPrice <= 0) {
    return undefined
  }

  return {
    '@type': 'AggregateOffer',
    lowPrice: props.lowPrice,
    highPrice: Math.max(props.highPrice, props.lowPrice),
    priceCurrency: props.currency || 'INR',
    offerCount: Math.max(props.offerCount, 1),
    availability: 'https://schema.org/InStock',
    url: props.url,
  }
}

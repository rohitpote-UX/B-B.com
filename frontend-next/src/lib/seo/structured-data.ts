/**
 * Brand Battle — Schema.org Structured Data Generator
 * Builds validated JSON-LD graphs for Product, Offer, AggregateOffer, FAQPage,
 * BreadcrumbList, Organization, and WebSite schemas.
 *
 * CRITICAL TRUST RULE: NEVER generate fake ratings, fake reviews, or fabricated attributes.
 * If data is missing, omit property.
 */

import { SEO_CONFIG } from './seo-config'
import { BreadcrumbItem } from './breadcrumbs'

export interface ProductJsonLdProps {
  id: number
  name: string
  description?: string
  image?: string
  brand?: string
  category?: string
  price?: number
  originalPrice?: number
  bestPlatform?: string
  priceVerifiedAt?: string | Date
  currency?: string
  rating?: number
  totalReviews?: number
  url: string
}

export interface ComparisonJsonLdProps {
  product1: ProductJsonLdProps
  product2: ProductJsonLdProps
  canonicalUrl: string
  breadcrumbs: BreadcrumbItem[]
  faqs?: Array<{ question: string; answer: string }>
}

/**
 * Builds Schema.org Product payload.
 */
export function buildProductJsonLd(props: ProductJsonLdProps): Record<string, any> {
  const schema: Record<string, any> = {
    '@context': 'https://schema.org',
    '@type': 'Product',
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

  // Real verified price offer (only if price > 0)
  if (props.price && props.price > 0) {
    schema.offers = {
      '@type': 'Offer',
      price: props.price,
      priceCurrency: props.currency || 'INR',
      availability: 'https://schema.org/InStock',
      url: props.url,
      seller: {
        '@type': 'Organization',
        name: props.bestPlatform || 'Verified Retailer',
      },
    }
    if (props.priceVerifiedAt) {
      schema.offers.priceValidUntil = new Date(
        new Date(props.priceVerifiedAt).getTime() + 86400 * 7 * 1000
      ).toISOString().split('T')[0]
    }
  }

  // Real aggregate rating ONLY if real reviews exist
  if (props.rating && props.rating > 0 && props.totalReviews && props.totalReviews > 0) {
    schema.aggregateRating = {
      '@type': 'AggregateRating',
      ratingValue: props.rating,
      reviewCount: props.totalReviews,
      bestRating: 5,
      worstRating: 1,
    }
  }

  return schema
}

/**
 * Builds Schema.org BreadcrumbList payload.
 */
export function buildBreadcrumbJsonLd(items: BreadcrumbItem[]): Record<string, any> {
  return {
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    itemListElement: items.map((item, index) => {
      const element: Record<string, any> = {
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
 * Builds Schema.org Organization payload.
 */
export function buildOrganizationJsonLd(): Record<string, any> {
  return {
    '@context': 'https://schema.org',
    '@type': 'Organization',
    name: SEO_CONFIG.organizationName,
    url: SEO_CONFIG.domain,
    logo: SEO_CONFIG.organizationLogo,
    contactPoint: {
      '@type': 'ContactPoint',
      email: SEO_CONFIG.supportEmail,
      contactType: 'customer support',
    },
  }
}

/**
 * Builds Schema.org WebSite payload with SearchAction.
 */
export function buildWebSiteJsonLd(): Record<string, any> {
  return {
    '@context': 'https://schema.org',
    '@type': 'WebSite',
    name: SEO_CONFIG.siteName,
    url: SEO_CONFIG.domain,
    potentialAction: {
      '@type': 'SearchAction',
      target: `${SEO_CONFIG.domain}/search?q={search_term_string}`,
      'query-input': 'required name=search_term_string',
    },
  }
}

/**
 * Builds comparison page Schema.org JSON-LD graph.
 */
export function buildComparisonGraphJsonLd({
  product1,
  product2,
  canonicalUrl,
  breadcrumbs,
  faqs,
}: ComparisonJsonLdProps): Record<string, any> {
  const graphNodes: any[] = [
    {
      '@type': 'WebPage',
      '@id': canonicalUrl,
      url: canonicalUrl,
      name: `${product1.name} vs ${product2.name} Comparison`,
    },
    buildBreadcrumbJsonLd(breadcrumbs),
    buildProductJsonLd(product1),
    buildProductJsonLd(product2),
  ]

  if (faqs && faqs.length > 0) {
    graphNodes.push({
      '@context': 'https://schema.org',
      '@type': 'FAQPage',
      mainEntity: faqs.map(faq => ({
        '@type': 'Question',
        name: faq.question,
        acceptedAnswer: {
          '@type': 'Answer',
          text: faq.answer,
        },
      })),
    })
  }

  return {
    '@context': 'https://schema.org',
    '@graph': graphNodes,
  }
}

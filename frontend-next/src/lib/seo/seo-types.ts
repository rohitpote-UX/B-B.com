/**
 * Brand Battle — Enterprise SEO Type Definitions
 * Strict TypeScript types for metadata, Schema.org entities, breadcrumbs,
 * indexability metrics, GEO/AEO answers, and SEO quality audit scores.
 */

export interface SeoConfig {
  siteName: string
  domain: string
  defaultTitle: string
  titleTemplate: string
  defaultDescription: string
  defaultOgImage: string
  twitterHandle: string
  locale: string
  organizationName: string
  organizationLogo: string
  supportEmail: string
}

export interface TitleProps {
  name: string
  brand?: string
  category?: string
  suffix?: string
}

export interface ComparisonTitleProps {
  product1Name: string
  product2Name: string
  category?: string
}

export interface ProductDescriptionProps {
  name: string
  brand?: string
  category?: string
  price?: number
  currency?: string
  specSnippet?: string
  dealScore?: number
  marketplaceCount?: number
}

export interface ComparisonDescriptionProps {
  product1Name: string
  product2Name: string
  category?: string
  price1?: number
  price2?: number
  currency?: string
  winnerName?: string
}

export interface BreadcrumbItem {
  name: string
  url: string
}

export interface EntitySeoMetrics {
  id: number
  name: string
  hasBrand: boolean
  hasCategory: boolean
  hasValidImage: boolean
  hasVerifiedPrice: boolean
  hasSpecs: boolean
  descriptionLength: number
  isDeleted?: boolean
}

export enum SeoEligibilityStatus {
  SEO_ELIGIBLE = 'SEO_ELIGIBLE',
  SEO_BLOCKED = 'SEO_BLOCKED',
  SEO_LOW_QUALITY = 'SEO_LOW_QUALITY',
  SEO_PENDING = 'SEO_PENDING',
}

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
  sku?: string
  mpn?: string
  gtin?: string
  specs?: Record<string, string | number>
  // ProductGroup / Variant relations for Google structured data
  productGroupId?: string
  productGroupName?: string
  variesBy?: string[]
  variantAttributes?: Record<string, string>
  siblingVariants?: Array<{ id: number; name: string; url: string; price?: number; sku?: string; image?: string }>
  offersList?: Array<{ price: number; originalPrice?: number; platform: string; url?: string; inStock?: boolean }>
}

export interface ComparisonJsonLdProps {
  product1: ProductJsonLdProps
  product2: ProductJsonLdProps
  canonicalUrl: string
  breadcrumbs: BreadcrumbItem[]
  faqs?: Array<{ question: string; answer: string }>
}

export interface FaqItem {
  question: string
  answer: string
}

export interface GeoFactSheet {
  entityName: string
  brand: string
  category: string
  verifiedPrice: number
  currency: string
  bestMarketplace: string
  priceVerifiedDate: string
  keySpecifications: Record<string, string | number>
  alternatives: string[]
  dealScore: number
  trustRating?: number
  verifiedReviewCount?: number
}

export interface AeoAnswerBlock {
  question: string
  directAnswer: string
  supportingFacts: string[]
  source: string
  verifiedAt: string
}

export interface InternalLinkRecommendation {
  text: string
  href: string
  relationship: 'product' | 'brand' | 'category' | 'comparison' | 'alternative'
  title: string
}

export interface SeoValidationResult {
  isValid: boolean
  score: number
  errors: string[]
  warnings: string[]
  passedChecks: string[]
}

/**
 * Brand Battle — Master Schema.org Structured Data Hub
 * Centralized entrypoint for generating validated JSON-LD graphs.
 * Strictly adheres to type safety and Trust-First data principles.
 */

import { ProductJsonLdProps, ComparisonJsonLdProps, BreadcrumbItem, FaqItem } from './seo-types'
import { buildProductSchema } from './product-schema'
import { buildOfferSchema, buildAggregateOfferSchema } from './offer-schema'
import { buildBreadcrumbSchema } from './breadcrumb-schema'
import { buildOrganizationSchema } from './organization-schema'
import { buildWebSiteSchema } from './website-schema'
import { buildFaqSchema } from './faq-schema'
import { buildComparisonSchema } from './comparison-schema'

export {
  buildProductSchema,
  buildOfferSchema,
  buildAggregateOfferSchema,
  buildBreadcrumbSchema,
  buildOrganizationSchema,
  buildWebSiteSchema,
  buildFaqSchema,
  buildComparisonSchema,
}

// Backward-compatible named aliases
export const buildProductJsonLd = buildProductSchema
export const buildBreadcrumbJsonLd = buildBreadcrumbSchema
export const buildOrganizationJsonLd = buildOrganizationSchema
export const buildWebSiteJsonLd = buildWebSiteSchema
export const buildComparisonGraphJsonLd = buildComparisonSchema

export type { ProductJsonLdProps, ComparisonJsonLdProps, BreadcrumbItem, FaqItem }

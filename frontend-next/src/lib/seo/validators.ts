/**
 * Brand Battle — Automated SEO Quality & Schema Validator
 * Validates metadata, canonicals, Schema.org JSON-LD objects, and ensures zero fake data violations.
 */

import { SeoValidationResult } from './seo-types'

/**
 * Runs validation checks on a page's SEO metadata and structured data payload.
 */
export function validatePageSeo(props: {
  title: string
  description: string
  canonicalUrl: string
  jsonLd?: Record<string, unknown>
  isIndexable?: boolean
}): SeoValidationResult {
  const errors: string[] = []
  const warnings: string[] = []
  const passedChecks: string[] = []

  // 1. Title Validation
  if (!props.title || props.title.trim().length === 0) {
    errors.push('Missing page title')
  } else if (props.title.length < 15) {
    warnings.push(`Page title is very short (${props.title.length} chars)`)
  } else if (props.title.length > 70) {
    warnings.push(`Page title may be truncated in search results (${props.title.length} chars)`)
  } else {
    passedChecks.push('Title length is optimal (15-70 chars)')
  }

  // 2. Meta Description Validation
  if (!props.description || props.description.trim().length === 0) {
    errors.push('Missing meta description')
  } else if (props.description.length < 50) {
    warnings.push(`Meta description is short (${props.description.length} chars)`)
  } else if (props.description.length > 170) {
    warnings.push(`Meta description may be truncated (${props.description.length} chars)`)
  } else {
    passedChecks.push('Meta description length is optimal (50-170 chars)')
  }

  // 3. Canonical URL Validation
  if (!props.canonicalUrl) {
    errors.push('Missing canonical URL')
  } else if (!props.canonicalUrl.startsWith('http://') && !props.canonicalUrl.startsWith('https://')) {
    errors.push('Canonical URL must be an absolute URL starting with http/https')
  } else if (props.canonicalUrl.includes('?') && !props.canonicalUrl.includes('category=') && !props.canonicalUrl.includes('brand=')) {
    warnings.push('Canonical URL contains query parameters')
  } else {
    passedChecks.push('Canonical URL is valid and absolute')
  }

  // 4. Schema.org JSON-LD Validation
  if (props.jsonLd) {
    if (props.jsonLd['@context'] !== 'https://schema.org') {
      errors.push('Schema.org @context must be "https://schema.org"')
    } else {
      passedChecks.push('Schema.org @context is valid')
    }

    // Check for fake rating violation: rating value without review count or rating > 5
    if (props.jsonLd.aggregateRating) {
      const agg = props.jsonLd.aggregateRating as Record<string, unknown>
      if (typeof agg.ratingValue === 'number' && (agg.ratingValue < 1 || agg.ratingValue > 5)) {
        errors.push(`Invalid ratingValue: ${agg.ratingValue} (must be between 1 and 5)`)
      }
      if (!agg.reviewCount || (typeof agg.reviewCount === 'number' && agg.reviewCount <= 0)) {
        errors.push('aggregateRating requires positive reviewCount')
      }
    }

    // Check Offer pricing validity
    if (props.jsonLd.offers) {
      const offer = props.jsonLd.offers as Record<string, unknown>
      if (typeof offer.price === 'number' && offer.price <= 0) {
        errors.push('Offer price must be greater than 0')
      }
    }
  }

  const score = Math.max(0, 100 - errors.length * 25 - warnings.length * 5)

  return {
    isValid: errors.length === 0,
    score,
    errors,
    warnings,
    passedChecks,
  }
}

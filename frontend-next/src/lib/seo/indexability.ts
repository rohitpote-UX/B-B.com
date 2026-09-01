/**
 * Brand Battle — Thin Content Protection & SEO Eligibility Engine
 * Evaluates entities deterministically to ensure only high-quality, verified products
 * and valid comparisons are exposed for search indexing.
 */

import { EntitySeoMetrics, SeoEligibilityStatus } from './seo-types'

export { SeoEligibilityStatus }

/**
 * Evaluates whether a product entity is eligible for search engine indexation.
 *
 * Rules:
 * - Must not be deleted or inactive
 * - Must have a valid name (> 2 chars)
 * - Must have a category or brand
 * - Must have a valid image URL
 * - Must have verified price or specs
 * - Description length must be >= 15 chars
 */
export function evaluateSeoEligibility(entity: EntitySeoMetrics): SeoEligibilityStatus {
  if (entity.isDeleted) {
    return SeoEligibilityStatus.SEO_BLOCKED
  }

  if (!entity.name || entity.name.trim().length < 3) {
    return SeoEligibilityStatus.SEO_LOW_QUALITY
  }

  if (!entity.hasBrand && !entity.hasCategory) {
    return SeoEligibilityStatus.SEO_LOW_QUALITY
  }

  if (!entity.hasValidImage) {
    return SeoEligibilityStatus.SEO_LOW_QUALITY
  }

  if (!entity.hasVerifiedPrice && !entity.hasSpecs) {
    return SeoEligibilityStatus.SEO_PENDING
  }

  if (entity.descriptionLength < 15) {
    return SeoEligibilityStatus.SEO_LOW_QUALITY
  }

  return SeoEligibilityStatus.SEO_ELIGIBLE
}

/**
 * Returns boolean whether an entity passes all SEO quality gates.
 */
export function isSeoEligible(entity: EntitySeoMetrics): boolean {
  return evaluateSeoEligibility(entity) === SeoEligibilityStatus.SEO_ELIGIBLE
}

/**
 * Evaluates whether a comparison pair is eligible for indexing.
 * Both products must exist, be SEO-eligible, and belong to comparable categories.
 */
export function isComparisonEligible(
  p1: EntitySeoMetrics | null | undefined,
  p2: EntitySeoMetrics | null | undefined,
  cat1?: string,
  cat2?: string
): boolean {
  if (!p1 || !p2) return false
  if (!isSeoEligible(p1) || !isSeoEligible(p2)) return false
  if (p1.id === p2.id) return false

  // Validate category compatibility
  if (cat1 && cat2) {
    const c1 = cat1.toLowerCase().trim()
    const c2 = cat2.toLowerCase().trim()
    return c1 === c2 || c1.includes(c2) || c2.includes(c1)
  }

  return true
}

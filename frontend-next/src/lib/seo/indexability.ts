/**
 * Brand Battle — Thin Content Protection & SEO Eligibility Engine
 * Evaluates entities deterministically to ensure only high-quality, verified products
 * are exposed for search indexing.
 */

export enum SeoEligibilityStatus {
  SEO_ELIGIBLE = 'SEO_ELIGIBLE',
  SEO_BLOCKED = 'SEO_BLOCKED',
  SEO_LOW_QUALITY = 'SEO_LOW_QUALITY',
  SEO_PENDING = 'SEO_PENDING',
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

/**
 * Evaluates whether a product entity is eligible for search engine indexation.
 *
 * Rules:
 * - Must not be deleted or inactive
 * - Must have a valid name (> 2 chars)
 * - Must have a category or brand
 * - Must have a valid image URL
 * - Must have verified price or specs
 * - Description length must be >= 20 chars
 */
export function evaluateSeoEligibility(entity: EntitySeoMetrics): SeoEligibilityStatus {
  if (entity.isDeleted) {
    return SeoEligibilityStatus.SEO_BLOCKED
  }

  if (!entity.name || entity.name.length < 3) {
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

export function isSeoEligible(entity: EntitySeoMetrics): boolean {
  return evaluateSeoEligibility(entity) === SeoEligibilityStatus.SEO_ELIGIBLE
}

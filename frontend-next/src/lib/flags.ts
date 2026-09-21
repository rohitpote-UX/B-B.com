/**
 * Brand Battle — Runtime Feature Flags Configuration
 * Enables controlled rollout, A/B isolation, and instant rollback.
 */

export interface FeatureFlags {
  LATEST_PRODUCTS_ENABLED: boolean
  FESTIVE_SHOPPING_BANNER_ENABLED: boolean
  GEO_FACTSHEETS_ENABLED: boolean
}

export const FEATURE_FLAGS: FeatureFlags = {
  // Master toggle for the homepage 'Latest Releases' section
  LATEST_PRODUCTS_ENABLED: process.env.NEXT_PUBLIC_LATEST_PRODUCTS_ENABLED !== 'false',

  // Subtle festive season context signal during Great Indian Festival & Big Billion Days 2026
  FESTIVE_SHOPPING_BANNER_ENABLED: process.env.NEXT_PUBLIC_FESTIVE_BANNER_ENABLED !== 'false',

  // Machine-readable GEO/AEO factsheet generator for AI search engines
  GEO_FACTSHEETS_ENABLED: true,
}

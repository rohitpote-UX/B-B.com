/**
 * Brand Battle — Enterprise SEO Configuration
 * Centralized domain settings, site metadata defaults, social card configs, and E-E-A-T trust signals.
 */

import { SeoConfig } from './seo-types'

export const SEO_CONFIG: SeoConfig = {
  siteName: 'Brand Battle',
  domain: process.env.NEXT_PUBLIC_APP_URL || 'https://brandbattle.in',
  defaultTitle: 'Brand Battle — Find The Best Product. Win Every Purchase.',
  titleTemplate: '%s — Brand Battle',
  defaultDescription:
    'AI-powered product intelligence, verified marketplace prices, price history tracking, and objective product comparisons across Amazon, Flipkart, Croma, and more. Verify before you spend.',
  defaultOgImage: 'https://brandbattle.in/og-default.png',
  twitterHandle: '@brandbattle',
  locale: 'en_IN',
  organizationName: 'Brand Battle Technologies Inc.',
  organizationLogo: 'https://brandbattle.in/logo.png',
  supportEmail: 'trust@brandbattle.in',
}

export type SeoConfigType = typeof SEO_CONFIG

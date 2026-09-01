/**
 * Brand Battle — Enterprise SEO Configuration
 * Centralized domain settings, site metadata defaults, and social card configs.
 */

export const SEO_CONFIG = {
  siteName: 'Brand Battle',
  domain: process.env.NEXT_PUBLIC_APP_URL || 'https://brandbattle.com',
  defaultTitle: 'Brand Battle — Find The Best Product. Win Every Purchase.',
  titleTemplate: '%s — Brand Battle',
  defaultDescription:
    'AI-powered product intelligence and product comparison platform. Compare verified marketplace prices, track price history, analyze specifications, and make confident purchase decisions.',
  defaultOgImage: 'https://brandbattle.com/og-default.png',
  twitterHandle: '@brandbattle',
  locale: 'en_IN',
  organizationName: 'Brand Battle Tech Inc.',
  organizationLogo: 'https://brandbattle.com/logo.png',
  supportEmail: 'trust@brandbattle.com',
}

export type SeoConfigType = typeof SEO_CONFIG

/**
 * Brand Battle — Schema.org WebSite Builder
 * Provides WebSite JSON-LD with Sitelinks SearchBox functionality for Google Search.
 */

import { SEO_CONFIG } from './seo-config'

export function buildWebSiteSchema(): Record<string, unknown> {
  return {
    '@context': 'https://schema.org',
    '@type': 'WebSite',
    '@id': `${SEO_CONFIG.domain}#website`,
    name: SEO_CONFIG.siteName,
    url: SEO_CONFIG.domain,
    description: SEO_CONFIG.defaultDescription,
    potentialAction: {
      '@type': 'SearchAction',
      target: `${SEO_CONFIG.domain}/search?q={search_term_string}`,
      'query-input': 'required name=search_term_string',
    },
  }
}

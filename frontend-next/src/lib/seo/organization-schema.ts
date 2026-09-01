/**
 * Brand Battle — Schema.org Organization Builder
 * Establishes publisher identity and E-E-A-T credibility for search engines.
 */

import { SEO_CONFIG } from './seo-config'

export function buildOrganizationSchema(): Record<string, unknown> {
  return {
    '@context': 'https://schema.org',
    '@type': 'Organization',
    '@id': `${SEO_CONFIG.domain}#organization`,
    name: SEO_CONFIG.organizationName,
    url: SEO_CONFIG.domain,
    logo: {
      '@type': 'ImageObject',
      url: SEO_CONFIG.organizationLogo,
      caption: SEO_CONFIG.organizationName,
    },
    contactPoint: {
      '@type': 'ContactPoint',
      email: SEO_CONFIG.supportEmail,
      contactType: 'customer support',
      areaServed: 'IN',
      availableLanguage: ['English', 'Hindi'],
    },
    sameAs: [
      `https://x.com/${SEO_CONFIG.twitterHandle.replace('@', '')}`,
    ],
  }
}

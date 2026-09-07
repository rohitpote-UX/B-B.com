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
    alternateName: 'BrandBattle',
    url: SEO_CONFIG.domain,
    logo: {
      '@type': 'ImageObject',
      url: SEO_CONFIG.organizationLogo,
      caption: 'Goldspade / BrandBattle',
    },
    contactPoint: {
      '@type': 'ContactPoint',
      email: SEO_CONFIG.supportEmail,
      telephone: '+91-8390612060',
      contactType: 'customer support and business inquiries',
      areaServed: 'IN',
      availableLanguage: ['English', 'Hindi'],
    },
    sameAs: [
      'https://x.com/GoldspadeFF',
    ],
  }
}

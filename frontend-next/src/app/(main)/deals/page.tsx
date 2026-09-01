import React from 'react'
import type { Metadata } from 'next'
import DealsClient from '@/components/deals/DealsClient'
import StructuredDataScript from '@/seo/structuredData'
import {
  SEO_CONFIG,
  buildDealsTitle,
  buildDealsDescription,
  buildRobotsDirectives,
  buildOpenGraphMetadata,
  buildBreadcrumbSchema,
} from '@/lib/seo'

export const metadata: Metadata = {
  title: buildDealsTitle(),
  description: buildDealsDescription(),
  alternates: {
    canonical: `${SEO_CONFIG.domain}/deals`,
  },
  robots: buildRobotsDirectives(),
  ...buildOpenGraphMetadata({
    title: buildDealsTitle(),
    description: buildDealsDescription(),
    url: `${SEO_CONFIG.domain}/deals`,
    type: 'website',
  }),
}

export default function DealsPage() {
  const breadcrumbJsonLd = buildBreadcrumbSchema([
    { name: 'Home', url: SEO_CONFIG.domain },
    { name: 'Deals', url: `${SEO_CONFIG.domain}/deals` },
  ])

  const collectionJsonLd = {
    '@context': 'https://schema.org',
    '@type': 'CollectionPage',
    name: 'Verified Discounts & Price Drops',
    description: buildDealsDescription(),
    url: `${SEO_CONFIG.domain}/deals`,
  }

  const combinedJsonLd = {
    '@context': 'https://schema.org',
    '@graph': [breadcrumbJsonLd, collectionJsonLd],
  }

  return (
    <>
      <StructuredDataScript jsonLd={combinedJsonLd} />
      <DealsClient />
    </>
  )
}

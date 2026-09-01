import React from 'react'
import type { Metadata } from 'next'
import DiscoverClient from '@/components/discover/DiscoverClient'
import StructuredDataScript from '@/seo/structuredData'
import {
  SEO_CONFIG,
  buildDiscoverTitle,
  buildRobotsDirectives,
  buildOpenGraphMetadata,
  buildBreadcrumbSchema,
} from '@/lib/seo'

export const metadata: Metadata = {
  title: buildDiscoverTitle(),
  description:
    'Discover curated products, trending electronics, and algorithmic price drops. Explore products with verified marketplace intelligence.',
  alternates: {
    canonical: `${SEO_CONFIG.domain}/discover`,
  },
  robots: buildRobotsDirectives(),
  ...buildOpenGraphMetadata({
    title: buildDiscoverTitle(),
    description: 'Discover curated products and price intelligence on Brand Battle.',
    url: `${SEO_CONFIG.domain}/discover`,
    type: 'website',
  }),
}

export default function DiscoverPage() {
  const breadcrumbJsonLd = buildBreadcrumbSchema([
    { name: 'Home', url: SEO_CONFIG.domain },
    { name: 'Discover', url: `${SEO_CONFIG.domain}/discover` },
  ])

  return (
    <>
      <StructuredDataScript jsonLd={breadcrumbJsonLd} />
      <DiscoverClient />
    </>
  )
}

import React from 'react'
import type { Metadata } from 'next'
import AIAdvisorClient from '@/components/ai/AIAdvisorClient'
import StructuredDataScript from '@/seo/structuredData'
import {
  SEO_CONFIG,
  buildRobotsDirectives,
  buildOpenGraphMetadata,
  buildBreadcrumbSchema,
} from '@/lib/seo'

export const metadata: Metadata = {
  title: 'AI Shopping Advisor & Recommendation Engine | Brand Battle',
  description:
    'Ask our AI shopping advisor anything about products, pricing, and comparisons. Powered by our 1,400+ product knowledge graph and verified multi-marketplace data.',
  alternates: {
    canonical: `${SEO_CONFIG.domain}/advisor`,
  },
  robots: buildRobotsDirectives(),
  ...buildOpenGraphMetadata({
    title: 'AI Shopping Advisor & Recommendation Engine | Brand Battle',
    description: 'Instant AI buying advice backed by real market intelligence and price verification.',
    url: `${SEO_CONFIG.domain}/advisor`,
    type: 'website',
  }),
}

export default function AIAdvisorPage() {
  const breadcrumbJsonLd = buildBreadcrumbSchema([
    { name: 'Home', url: SEO_CONFIG.domain },
    { name: 'AI Advisor', url: `${SEO_CONFIG.domain}/advisor` },
  ])

  return (
    <>
      <StructuredDataScript jsonLd={breadcrumbJsonLd} />
      <AIAdvisorClient />
    </>
  )
}

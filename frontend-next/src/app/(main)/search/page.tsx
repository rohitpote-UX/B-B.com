import React, { Suspense } from 'react'
import type { Metadata } from 'next'
import SearchClient from '@/components/search/SearchClient'
import StructuredDataScript from '@/seo/structuredData'
import {
  SEO_CONFIG,
  buildSearchTitle,
  buildRobotsDirectives,
  buildBreadcrumbSchema,
} from '@/lib/seo'

export const metadata: Metadata = {
  title: buildSearchTitle(),
  description:
    'Search the Brand Battle catalog for verified electronics, smartphones, headphones, laptops, and authentic marketplace deals.',
  alternates: {
    canonical: `${SEO_CONFIG.domain}/search`,
  },
  robots: buildRobotsDirectives({ isIndexable: true }),
}

export default function SearchPage() {
  const breadcrumbJsonLd = buildBreadcrumbSchema([
    { name: 'Home', url: SEO_CONFIG.domain },
    { name: 'Search', url: `${SEO_CONFIG.domain}/search` },
  ])

  return (
    <>
      <StructuredDataScript jsonLd={breadcrumbJsonLd} />
      <Suspense fallback={<div className="min-h-screen pt-32 pb-40 text-center text-theme-muted">Loading search catalog...</div>}>
        <SearchClient />
      </Suspense>
    </>
  )
}

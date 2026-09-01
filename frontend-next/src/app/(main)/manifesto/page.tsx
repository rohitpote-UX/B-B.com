import React from 'react'
import type { Metadata } from 'next'
import ManifestoClient from '@/components/manifesto/ManifestoClient'
import StructuredDataScript from '@/seo/structuredData'
import {
  SEO_CONFIG,
  buildRobotsDirectives,
  buildOpenGraphMetadata,
  buildBreadcrumbSchema,
} from '@/lib/seo'

export const metadata: Metadata = {
  title: 'The Brand Battle Manifesto — The Most Trusted Product Verification Platform',
  description:
    'Why we built Brand Battle: How e-commerce failed consumers with fake discounts and sponsored pollution, and how objective AI product intelligence restores truth to online shopping.',
  alternates: {
    canonical: `${SEO_CONFIG.domain}/manifesto`,
  },
  robots: buildRobotsDirectives(),
  ...buildOpenGraphMetadata({
    title: 'The Brand Battle Manifesto — Trust Comes First in AI Shopping',
    description: 'Our core philosophy: Objective product intelligence with zero sponsored manipulation.',
    url: `${SEO_CONFIG.domain}/manifesto`,
    type: 'article',
  }),
}

export default function ManifestoPage() {
  const breadcrumbJsonLd = buildBreadcrumbSchema([
    { name: 'Home', url: SEO_CONFIG.domain },
    { name: 'Manifesto', url: `${SEO_CONFIG.domain}/manifesto` },
  ])

  const articleJsonLd = {
    '@context': 'https://schema.org',
    '@type': 'AboutPage',
    name: 'The Brand Battle Manifesto',
    description:
      'Our core philosophy: Objective product intelligence, price verification, and decision clarity with zero sponsored manipulation.',
    url: `${SEO_CONFIG.domain}/manifesto`,
    publisher: {
      '@type': 'Organization',
      name: SEO_CONFIG.organizationName,
      logo: SEO_CONFIG.organizationLogo,
    },
  }

  const combinedJsonLd = {
    '@context': 'https://schema.org',
    '@graph': [breadcrumbJsonLd, articleJsonLd],
  }

  return (
    <>
      <StructuredDataScript jsonLd={combinedJsonLd} />
      <ManifestoClient />
    </>
  )
}

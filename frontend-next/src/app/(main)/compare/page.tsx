import React from 'react'
import type { Metadata } from 'next'
import CompareWorkspaceClient from '@/components/compare/CompareWorkspaceClient'
import { SEO_CONFIG, buildRobotsDirectives, buildOpenGraphMetadata } from '@/lib/seo'

export const metadata: Metadata = {
  title: 'Head-to-Head AI Product Comparison & Decision Engine | Brand Battle',
  description:
    'Compare any two products side-by-side. Unbiased 5-system AI consensus evaluation, hardware specifications breakdown, 5-year total ownership cost, and verified live marketplace pricing.',
  alternates: {
    canonical: `${SEO_CONFIG.domain}/compare`,
  },
  robots: buildRobotsDirectives(),
  ...buildOpenGraphMetadata({
    title: 'Head-to-Head AI Product Comparison & Decision Engine | Brand Battle',
    description: 'Compare products side-by-side with verified pricing and AI decision scoring.',
    url: `${SEO_CONFIG.domain}/compare`,
    type: 'website',
  }),
}

export default function ComparePage() {
  return <CompareWorkspaceClient />
}

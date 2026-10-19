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

function CompareSkeleton() {
  return (
    <div className="w-full max-w-[1536px] mx-auto px-4 sm:px-8 py-10 animate-pulse">
      <div className="h-10 w-64 bg-white/5 rounded-xl mb-8" />
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div className="h-96 rounded-3xl bg-white/[0.02] border border-white/10 p-8" />
        <div className="h-96 rounded-3xl bg-white/[0.02] border border-white/10 p-8" />
      </div>
    </div>
  )
}

export default function ComparePage() {
  return (
    <React.Suspense fallback={<CompareSkeleton />}>
      <CompareWorkspaceClient />
    </React.Suspense>
  )
}

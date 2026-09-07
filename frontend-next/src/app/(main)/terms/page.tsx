import React from 'react'
import type { Metadata } from 'next'
import StructuredDataScript from '@/seo/structuredData'
import { SEO_CONFIG, buildBreadcrumbSchema } from '@/lib/seo'

export const metadata: Metadata = {
  title: 'Terms of Service — Transparent User Agreement | BrandBattle',
  description:
    'Terms of Service for BrandBattle. Understand our commercial disclosures, affiliate relationships, intellectual property rights, and terms of use.',
  alternates: {
    canonical: `${SEO_CONFIG.domain}/terms`,
  },
}

export default function TermsPage() {
  const breadcrumbs = buildBreadcrumbSchema([
    { name: 'Home', url: SEO_CONFIG.domain },
    { name: 'Terms of Service', url: `${SEO_CONFIG.domain}/terms` },
  ])

  return (
    <div className="min-h-screen bg-[#050505] text-white pt-32 pb-40">
      <StructuredDataScript jsonLd={breadcrumbs} />
      <div className="w-full max-w-[1000px] mx-auto px-6 md:px-12">
        <div className="mb-16">
          <span className="text-[0.75rem] font-semibold uppercase tracking-[0.25em] text-[#f20ab0] block mb-4">
            Legal & Trust
          </span>
          <h1 className="text-4xl sm:text-5xl font-bold font-[var(--font-display)] tracking-tight mb-4">
            Terms of Service
          </h1>
          <p className="text-sm text-[#71717a]">Last Updated: September 2026</p>
        </div>

        <div className="space-y-12 text-[#a1a1aa] leading-relaxed text-[1.05rem]">
          <section>
            <h2 className="text-2xl font-bold font-[var(--font-display)] text-white mb-4">1. Acceptance of Terms</h2>
            <p>
              By accessing or using BrandBattle (https://brandbattle.in), you agree to be bound by these Terms of Service. If you do not agree, please discontinue use of our platform immediately.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold font-[var(--font-display)] text-white mb-4">2. Commercial & Affiliate Transparency</h2>
            <p className="mb-4">
              BrandBattle operates as an independent price comparison and verification engine. To support our infrastructure:
            </p>
            <ul className="list-disc pl-6 space-y-2">
              <li>Some outbound links to retailers (e.g. Amazon, Flipkart, Croma, Myntra) are affiliate links. If you purchase through these links, we may earn an affiliate commission.</li>
              <li><strong className="text-white">Editorial Independence:</strong> Affiliate partnerships never dictate or influence our Deal Scores, price anomaly detection, or comparison algorithms. The lowest verified price always wins.</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-bold font-[var(--font-display)] text-white mb-4">3. Accuracy & Verification Disclaimer</h2>
            <p>
              While we run multi-stage automated verification pipelines to capture live prices, e-commerce marketplace prices fluctuate continuously. Always confirm the final checkout price and terms on the merchant&apos;s site prior to payment.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold font-[var(--font-display)] text-white mb-4">4. Permitted Use</h2>
            <p>
              BrandBattle is provided for personal, non-commercial consumer research. Automated scraping, extraction, or republication of our normalized specifications and proprietary deal scores without prior written consent is strictly prohibited.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold font-[var(--font-display)] text-white mb-4">5. Governing Law</h2>
            <p>
              These Terms shall be governed by and construed in accordance with the laws of India, subject to the exclusive jurisdiction of the courts of Maharashtra, India.
            </p>
          </section>
        </div>
      </div>
    </div>
  )
}

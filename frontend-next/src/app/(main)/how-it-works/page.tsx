import React from 'react'
import type { Metadata } from 'next'
import Link from 'next/link'
import { Cpu, RefreshCw, BarChart2, CheckCircle2, ArrowRight } from 'lucide-react'
import StructuredDataScript from '@/seo/structuredData'
import { SEO_CONFIG, buildBreadcrumbSchema } from '@/lib/seo'

export const metadata: Metadata = {
  title: 'How It Works — Algorithmic Price Aggregation & Verification | BrandBattle',
  description:
    'Discover how BrandBattle aggregates, normalizes, and verifies real-time product prices across Amazon, Flipkart, Croma, and Reliance Digital.',
  alternates: {
    canonical: `${SEO_CONFIG.domain}/how-it-works`,
  },
}

export default function HowItWorksPage() {
  const breadcrumbs = buildBreadcrumbSchema([
    { name: 'Home', url: SEO_CONFIG.domain },
    { name: 'How It Works', url: `${SEO_CONFIG.domain}/how-it-works` },
  ])

  const steps = [
    {
      number: '01',
      icon: Cpu,
      title: 'Real-Time Ingestion & Extraction',
      desc: 'Our pipeline tracks canonical product identities across major Indian e-commerce marketplaces including Amazon, Flipkart, Croma, and Reliance Digital, collecting price, stock status, delivery speed, and seller reputation.',
    },
    {
      number: '02',
      icon: BarChart2,
      title: 'Mathematical Anomaly Detection',
      desc: 'Observed prices are benchmarked against 90-day historical moving averages. Any price drop or spike exceeding 40% is immediately quarantined to prevent misprints or seller fraud from skewing recommendations.',
    },
    {
      number: '03',
      icon: RefreshCw,
      title: 'Deterministic Freshness Tiers',
      desc: 'High-intent trending items are refreshed every 30 minutes (HOT Tier). Standard products update every 6 hours, while long-tail catalog items refresh within 24 hours to ensure high fidelity without rate-limit saturation.',
    },
    {
      number: '04',
      icon: CheckCircle2,
      title: 'Consensus & Trust Scoring',
      desc: 'The Deal Score (0–100) calculates price delta, seller reliability, return window guarantees, and historical stability into a single, transparent metric.',
    },
  ]

  return (
    <div className="min-h-screen bg-[#050505] text-white pt-32 pb-40">
      <StructuredDataScript jsonLd={breadcrumbs} />
      <div className="w-full max-w-[1400px] mx-auto px-6 md:px-12">
        <div className="max-w-4xl mb-24">
          <span className="text-[0.75rem] font-semibold uppercase tracking-[0.25em] text-[#f20ab0] block mb-6">
            Architecture & Pipeline
          </span>
          <h1 className="text-[3rem] sm:text-[4.5rem] lg:text-[5.5rem] font-bold font-[var(--font-display)] tracking-tight leading-[1.05] mb-8">
            How BrandBattle <br className="hidden sm:block" />
            Verifies Prices.
          </h1>
          <p className="text-[1.15rem] sm:text-[1.35rem] leading-[1.6] text-[#a1a1aa] font-light">
            We do not rely on marketplace self-reported discounts. We run a deterministic four-stage verification pipeline that validates every offer before presenting it to you.
          </p>
        </div>

        {/* Step-by-Step Flow */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-32">
          {steps.map((s, idx) => {
            const Icon = s.icon
            return (
              <div
                key={idx}
                className="p-8 sm:p-12 rounded-3xl bg-[#0c0c0e] border border-[#1a1a20] relative"
              >
                <div className="flex items-center justify-between mb-8">
                  <div className="w-12 h-12 rounded-2xl bg-[#f20ab0]/10 flex items-center justify-center text-[#f20ab0]">
                    <Icon className="w-6 h-6" />
                  </div>
                  <span className="text-3xl font-bold font-[var(--font-display)] text-white/20">
                    {s.number}
                  </span>
                </div>
                <h2 className="text-2xl font-bold font-[var(--font-display)] mb-4">{s.title}</h2>
                <p className="text-[#8e8e93] leading-relaxed">{s.desc}</p>
              </div>
            )
          })}
        </div>

        {/* CTA */}
        <div className="text-center p-12 rounded-3xl bg-[#0c0c0e] border border-[#1a1a20]">
          <h2 className="text-3xl font-bold font-[var(--font-display)] mb-4">Want to see it in action?</h2>
          <p className="text-[#8e8e93] max-w-xl mx-auto mb-8">
            Explore our live comparison matrix or inspect verified price trends on any product.
          </p>
          <div className="flex justify-center gap-4">
            <Link
              href="/compare"
              className="inline-flex items-center gap-2 px-8 py-3.5 rounded-full bg-[#f20ab0] text-white text-sm font-semibold hover:bg-[#d6099c] transition-colors"
            >
              <span>Explore Comparisons</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}

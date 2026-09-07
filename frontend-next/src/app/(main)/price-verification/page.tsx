import React from 'react'
import type { Metadata } from 'next'
import Link from 'next/link'
import { ShieldAlert, Clock, Image as ImageIcon, CheckCheck, ArrowRight } from 'lucide-react'
import StructuredDataScript from '@/seo/structuredData'
import { SEO_CONFIG, buildBreadcrumbSchema } from '@/lib/seo'

export const metadata: Metadata = {
  title: 'Price Verification Framework & Trust Standards | BrandBattle',
  description:
    'Technical documentation of BrandBattle’s Data Trust Hardening system: 40% price anomaly quarantine, TTL freshness tiers, and image validation protocols.',
  alternates: {
    canonical: `${SEO_CONFIG.domain}/price-verification`,
  },
}

export default function PriceVerificationPage() {
  const breadcrumbs = buildBreadcrumbSchema([
    { name: 'Home', url: SEO_CONFIG.domain },
    { name: 'Price Verification', url: `${SEO_CONFIG.domain}/price-verification` },
  ])

  const tiers = [
    {
      tier: 'HOT TIER',
      ttl: '30 Minutes',
      criteria: 'Products with active price alerts, high velocity views (>1,000/day), or major festival sales.',
      color: '#f20ab0',
    },
    {
      tier: 'STANDARD TIER',
      ttl: '6 Hours',
      criteria: 'Active catalog products across electronics, smartphones, laptops, and audio gear.',
      color: '#06b6d4',
    },
    {
      tier: 'LOW PRIORITY TIER',
      ttl: '24 Hours',
      criteria: 'Niche, seasonal, or legacy items with stable historical pricing patterns.',
      color: '#10b981',
    },
  ]

  return (
    <div className="min-h-screen bg-[#050505] text-white pt-32 pb-40">
      <StructuredDataScript jsonLd={breadcrumbs} />
      <div className="w-full max-w-[1400px] mx-auto px-6 md:px-12">
        <div className="max-w-4xl mb-24">
          <span className="text-[0.75rem] font-semibold uppercase tracking-[0.25em] text-[#f20ab0] block mb-6">
            Data Trust Hardening
          </span>
          <h1 className="text-[3rem] sm:text-[4.5rem] lg:text-[5.5rem] font-bold font-[var(--font-display)] tracking-tight leading-[1.05] mb-8">
            Price Verification <br className="hidden sm:block" />
            Framework.
          </h1>
          <p className="text-[1.15rem] sm:text-[1.35rem] leading-[1.6] text-[#a1a1aa] font-light">
            Our core positioning is: <span className="text-white font-medium">&quot;The most trusted place to verify any product before you spend your money.&quot;</span>
            <br />
            Data accuracy is prioritized over raw listing volume. Here is how our safeguards operate.
          </p>
        </div>

        {/* Section 1: Anomaly Detection */}
        <div className="p-8 sm:p-12 rounded-3xl bg-[#0c0c0e] border border-[#1a1a20] mb-12">
          <div className="flex items-center gap-4 mb-6 text-[#f20ab0]">
            <ShieldAlert className="w-8 h-8" />
            <h2 className="text-2xl sm:text-3xl font-bold font-[var(--font-display)] text-white">
              Price Anomaly Quarantine (40% Rule)
            </h2>
          </div>
          <p className="text-[#a1a1aa] leading-relaxed mb-6">
            Marketplaces frequently suffer from seller pricing errors, counterfeit flash listings, or currency glitches (e.g. ₹99,999 laptop listed at ₹999).
          </p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-sm">
            <div className="p-6 rounded-2xl bg-[#050505] border border-[#1f1f28]">
              <span className="text-xs uppercase tracking-widest text-[#f20ab0] font-semibold block mb-2">Sudden Drops</span>
              <p className="text-[#71717a]">Any observed price dropping &gt;40% below 30-day baseline is immediately marked &apos;quarantined&apos; until re-verified.</p>
            </div>
            <div className="p-6 rounded-2xl bg-[#050505] border border-[#1f1f28]">
              <span className="text-xs uppercase tracking-widest text-[#f20ab0] font-semibold block mb-2">Sudden Spikes</span>
              <p className="text-[#71717a]">Inflated &quot;original MRPs&quot; introduced right before festival sales are flagged to prevent fake discount claims.</p>
            </div>
            <div className="p-6 rounded-2xl bg-[#050505] border border-[#1f1f28]">
              <span className="text-xs uppercase tracking-widest text-[#f20ab0] font-semibold block mb-2">Impossible Values</span>
              <p className="text-[#71717a]">Zero, negative, or currency-mismatched prices are discarded at parser level with failure logging.</p>
            </div>
          </div>
        </div>

        {/* Section 2: Freshness Tiers */}
        <div className="p-8 sm:p-12 rounded-3xl bg-[#0c0c0e] border border-[#1a1a20] mb-12">
          <div className="flex items-center gap-4 mb-6 text-[#06b6d4]">
            <Clock className="w-8 h-8" />
            <h2 className="text-2xl sm:text-3xl font-bold font-[var(--font-display)] text-white">
              Deterministic Freshness Tiers
            </h2>
          </div>
          <p className="text-[#a1a1aa] leading-relaxed mb-8">
            Every product displays its exact verification timestamp. When an offer exceeds its Tier TTL, its status transitions from &apos;verified&apos; to &apos;recently verified&apos; or &apos;stale&apos;.
          </p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {tiers.map((t, idx) => (
              <div key={idx} className="p-6 rounded-2xl bg-[#050505] border border-[#1f1f28]">
                <div className="flex items-center justify-between mb-4">
                  <span className="text-xs font-semibold uppercase tracking-widest" style={{ color: t.color }}>{t.tier}</span>
                  <span className="text-xs px-2.5 py-1 rounded-full bg-white/5 text-white font-mono">{t.ttl}</span>
                </div>
                <p className="text-sm text-[#71717a]">{t.criteria}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Section 3: Image Verification */}
        <div className="p-8 sm:p-12 rounded-3xl bg-[#0c0c0e] border border-[#1a1a20]">
          <div className="flex items-center gap-4 mb-6 text-[#10b981]">
            <ImageIcon className="w-8 h-8" />
            <h2 className="text-2xl sm:text-3xl font-bold font-[var(--font-display)] text-white">
              Image Verification & Fallback Recovery
            </h2>
          </div>
          <p className="text-[#a1a1aa] leading-relaxed mb-4">
            Marketplace CDNs frequently invalidate thumbnail URLs after promotions end. Our engine executes HTTP HEAD checks, validates MIME types (`image/jpeg`, `image/webp`), detects placeholder graphics, and automatically triggers high-resolution fallback recovery.
          </p>
        </div>
      </div>
    </div>
  )
}

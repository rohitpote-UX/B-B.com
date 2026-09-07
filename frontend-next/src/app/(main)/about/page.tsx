import React from 'react'
import type { Metadata } from 'next'
import Link from 'next/link'
import { ShieldCheck, Target, Eye, Award, ArrowRight } from 'lucide-react'
import StructuredDataScript from '@/seo/structuredData'
import { SEO_CONFIG, buildBreadcrumbSchema } from '@/lib/seo'

export const metadata: Metadata = {
  title: 'About BrandBattle — The Most Trusted Place to Verify Any Product',
  description:
    'Learn about BrandBattle’s mission to bring radical transparency and algorithmic price verification to Indian e-commerce. Verify before you spend.',
  alternates: {
    canonical: `${SEO_CONFIG.domain}/about`,
  },
}

export default function AboutPage() {
  const breadcrumbs = buildBreadcrumbSchema([
    { name: 'Home', url: SEO_CONFIG.domain },
    { name: 'About', url: `${SEO_CONFIG.domain}/about` },
  ])

  const aboutJsonLd = {
    '@context': 'https://schema.org',
    '@type': 'AboutPage',
    name: 'About BrandBattle',
    description:
      'BrandBattle is an independent product verification and price intelligence platform dedicated to protecting consumers from fake discounts, manipulated ratings, and deceptive marketplace practices.',
    url: `${SEO_CONFIG.domain}/about`,
  }

  const combinedJsonLd = {
    '@context': 'https://schema.org',
    '@graph': [breadcrumbs, aboutJsonLd],
  }

  const pillars = [
    {
      icon: ShieldCheck,
      title: 'Algorithmic Independence',
      desc: 'We never accept payment to inflate a product’s rank, score, or recommendation. Every deal score is computed mathematically against 90-day price history.',
    },
    {
      icon: Eye,
      title: 'Zero Fake Discount Tolerance',
      desc: 'Inflated MRPs and artificial "80% off" claims are automatically flagged and quarantined by our verification engine before reaching consumers.',
    },
    {
      icon: Target,
      title: 'Cross-Marketplace Consensus',
      desc: 'We monitor prices across Amazon, Flipkart, Croma, and Reliance Digital to detect genuine price drops and identify true all-time lows.',
    },
    {
      icon: Award,
      title: 'Category-Locked Advice',
      desc: 'Our recommendation engine respects strict compatibility boundaries. We never push unrelated products just because they yield higher commission.',
    },
  ]

  return (
    <div className="min-h-screen bg-[#050505] text-white pt-32 pb-40">
      <StructuredDataScript jsonLd={combinedJsonLd} />
      <div className="w-full max-w-[1400px] mx-auto px-6 md:px-12">
        {/* Editorial Hero */}
        <div className="max-w-4xl mb-24">
          <span className="text-[0.75rem] font-semibold uppercase tracking-[0.25em] text-[#f20ab0] block mb-6">
            Our Mission & Principles
          </span>
          <h1 className="text-[3rem] sm:text-[4.5rem] lg:text-[5.5rem] font-bold font-[var(--font-display)] tracking-tight leading-[1.05] mb-8">
            The Most Trusted Place <br className="hidden sm:block" />
            To Verify Any Product.
          </h1>
          <p className="text-[1.15rem] sm:text-[1.35rem] leading-[1.6] text-[#a1a1aa] font-light">
            E-commerce in India is flooded with manufactured urgency, synthetic reviews, and fake markups.
            BrandBattle exists to restore trust by giving shoppers verifiable data before they spend their hard-earned money.
          </p>
        </div>

        {/* Pillars Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-32">
          {pillars.map((p, idx) => {
            const Icon = p.icon
            return (
              <div
                key={idx}
                className="p-8 sm:p-12 rounded-3xl bg-[#0c0c0e] border border-[#1a1a20] hover:border-[#2a2a35] transition-all"
              >
                <div className="w-12 h-12 rounded-2xl bg-[#f20ab0]/10 flex items-center justify-center text-[#f20ab0] mb-6">
                  <Icon className="w-6 h-6" />
                </div>
                <h2 className="text-2xl font-bold font-[var(--font-display)] mb-4">{p.title}</h2>
                <p className="text-[#8e8e93] leading-relaxed">{p.desc}</p>
              </div>
            )
          })}
        </div>

        {/* Commitment Statement */}
        <div className="p-10 sm:p-16 rounded-3xl bg-gradient-to-br from-[#121218] to-[#0a0a0f] border border-[#222230] relative overflow-hidden">
          <div className="max-w-2xl">
            <h2 className="text-3xl sm:text-4xl font-bold font-[var(--font-display)] mb-6">
              Our Promise to Indian Shoppers
            </h2>
            <p className="text-[#a1a1aa] leading-relaxed mb-8">
              Every timestamp, price observation, and discount percentage shown on BrandBattle is verified against actual marketplace state. If we cannot prove a price is real, we quarantine it.
            </p>
            <div className="flex flex-wrap gap-4">
              <Link
                href="/price-verification"
                className="inline-flex items-center gap-2 px-6 py-3 rounded-full bg-[#f20ab0] text-white text-sm font-semibold hover:bg-[#d6099c] transition-colors"
              >
                <span>Read Verification Framework</span>
                <ArrowRight className="w-4 h-4" />
              </Link>
              <Link
                href="/team"
                className="inline-flex items-center gap-2 px-6 py-3 rounded-full bg-white/5 border border-white/10 text-white text-sm font-semibold hover:bg-white/10 transition-colors"
              >
                <span>Meet the Team</span>
              </Link>
              <Link
                href="/contact"
                className="inline-flex items-center gap-2 px-6 py-3 rounded-full bg-white/5 border border-white/10 text-white text-sm font-semibold hover:bg-white/10 transition-colors"
              >
                <span>Get in Touch</span>
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

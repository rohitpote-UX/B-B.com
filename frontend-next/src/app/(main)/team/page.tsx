import React from 'react'
import type { Metadata } from 'next'
import Link from 'next/link'
import { Sparkles, ShieldCheck, ArrowRight, Building2 } from 'lucide-react'
import StructuredDataScript from '@/seo/structuredData'
import { SEO_CONFIG, buildBreadcrumbSchema } from '@/lib/seo'
import TeamCardList from './TeamCardList'

export const metadata: Metadata = {
  title: 'Team — BrandBattle | Goldspade',
  description: 'Meet the team behind BrandBattle at Goldspade.',
  alternates: {
    canonical: `${SEO_CONFIG.domain}/team`,
  },
  openGraph: {
    title: 'Team — BrandBattle | Goldspade',
    description: 'Meet the team behind BrandBattle at Goldspade.',
    url: `${SEO_CONFIG.domain}/team`,
    siteName: 'Brand Battle',
    locale: 'en_IN',
    type: 'website',
  },
  twitter: {
    card: 'summary',
    title: 'Team — BrandBattle | Goldspade',
    description: 'Meet the team behind BrandBattle at Goldspade.',
    creator: '@GoldspadeFF',
  },
}

export interface TeamMember {
  name: string
  position: string
  company: string
  product: string
  initials: string
  imageSrc: string
  bio?: string
}

const TEAM_MEMBERS: TeamMember[] = [
  {
    name: 'Rohit Pote',
    position: 'Founder & CEO',
    company: 'Goldspade',
    product: 'BrandBattle',
    initials: 'RP',
    imageSrc: '/team/rohit-pote.jpg',
    bio: 'Directing strategic vision, core platform architecture, and product governance for BrandBattle under Goldspade.',
  },
  {
    name: 'Tejas Salunkhe',
    position: 'CTO',
    company: 'Goldspade',
    product: 'BrandBattle',
    initials: 'TS',
    imageSrc: '/team/tejas-salunkhe.jpg',
    bio: 'Leading engineering infrastructure, distributed scraper networks, and mathematical price verification pipelines.',
  },
  {
    name: 'Abhijeet Patale',
    position: 'CFO',
    company: 'Goldspade',
    product: 'BrandBattle',
    initials: 'AP',
    imageSrc: '/team/abhijeet-patale.jpg',
    bio: 'Overseeing financial strategy, commercial partnerships, resource allocation, and operational growth.',
  },
  {
    name: 'Shivraj Desai',
    position: 'COO',
    company: 'Goldspade',
    product: 'BrandBattle',
    initials: 'SD',
    imageSrc: '/team/shivraj-desai.jpg',
    bio: 'Managing cross-functional platform operations, data pipeline reliability, and retailer partner integration.',
  },
]

export default function TeamPage() {
  const breadcrumbs = buildBreadcrumbSchema([
    { name: 'Home', url: SEO_CONFIG.domain },
    { name: 'Team', url: `${SEO_CONFIG.domain}/team` },
  ])

  const teamJsonLd = {
    '@context': 'https://schema.org',
    '@type': 'AboutPage',
    name: 'Team — BrandBattle | Goldspade',
    url: `${SEO_CONFIG.domain}/team`,
    description: 'Meet the team behind BrandBattle at Goldspade.',
    mainEntity: {
      '@type': 'Organization',
      name: 'Goldspade',
      alternateName: 'BrandBattle',
      url: SEO_CONFIG.domain,
      logo: SEO_CONFIG.organizationLogo,
      employee: TEAM_MEMBERS.map((member) => ({
        '@type': 'Person',
        name: member.name,
        jobTitle: member.position,
        worksFor: {
          '@type': 'Organization',
          name: member.company,
        },
      })),
    },
  }

  const combinedJsonLd = {
    '@context': 'https://schema.org',
    '@graph': [breadcrumbs, teamJsonLd],
  }

  return (
    <div className="min-h-screen bg-[#050505] text-white pt-32 pb-40">
      <StructuredDataScript jsonLd={combinedJsonLd} />

      <div className="w-full max-w-[1400px] mx-auto px-6 md:px-12">
        {/* Editorial Header */}
        <div className="max-w-4xl mb-20">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#ff1695]/10 border border-[#ff1695]/20 text-[#ff1695] text-xs font-semibold uppercase tracking-[0.2em] mb-6">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Executive Leadership & Team</span>
          </div>
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold font-[var(--font-display)] tracking-tight uppercase leading-[1.05] mb-6">
            THE PEOPLE BEHIND <span className="text-[#ff1695] italic">BRANDBATTLE.</span>
          </h1>
          <p className="text-lg sm:text-xl text-[#a1a1aa] leading-relaxed font-light max-w-3xl">
            Meet the team building BrandBattle under Goldspade — focused on making product research clearer, more transparent, and more trustworthy.
          </p>
        </div>

        {/* 4-Card Team Grid */}
        <div className="mb-24">
          <TeamCardList members={TEAM_MEMBERS} />
        </div>

        {/* Supporting Trust & Governance Card */}
        <div className="p-8 sm:p-12 rounded-3xl bg-gradient-to-br from-[#0c0c0e] to-[#070709] border border-[#1a1a20] flex flex-col md:flex-row items-start md:items-center justify-between gap-8">
          <div className="max-w-2xl">
            <div className="inline-flex items-center gap-2 text-xs font-mono uppercase tracking-widest text-[#ff1695] mb-3">
              <Building2 className="w-4 h-4" />
              <span>A Goldspade Platform</span>
            </div>
            <h2 className="text-2xl font-bold font-[var(--font-display)] mb-3 text-white">
              Built on Uncompromising Transparency
            </h2>
            <p className="text-sm text-[#8e8e93] leading-relaxed">
              Every member of our leadership team is committed to objective data. We maintain a strict zero-paid-for-rank policy: no brand can pay to alter comparison verdicts, inflate deal scores, or fabricate ratings on BrandBattle.
            </p>
          </div>

          <div className="flex flex-wrap gap-4 shrink-0">
            <Link
              href="/about"
              className="inline-flex items-center gap-2 px-6 py-3 rounded-full bg-white text-black text-xs sm:text-sm font-semibold hover:bg-white/90 transition-colors"
            >
              <span>Our Principles</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
            <Link
              href="/contact"
              className="inline-flex items-center gap-2 px-6 py-3 rounded-full bg-white/5 border border-white/10 text-white text-xs sm:text-sm font-semibold hover:bg-white/10 transition-colors"
            >
              <span>Contact Team</span>
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}

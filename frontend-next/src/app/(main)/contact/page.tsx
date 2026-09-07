import React from 'react'
import type { Metadata } from 'next'
import { Mail, Phone, ArrowUpRight, ShieldAlert, Sparkles, Building2, UserCheck } from 'lucide-react'
import StructuredDataScript from '@/seo/structuredData'
import { SEO_CONFIG, buildBreadcrumbSchema } from '@/lib/seo'

export const metadata: Metadata = {
  title: 'Contact BrandBattle | Get in Touch with Goldspade',
  description:
    'Have a question, feedback, partnership idea or issue with BrandBattle? Contact the Goldspade team.',
  alternates: {
    canonical: `${SEO_CONFIG.domain}/contact`,
  },
  openGraph: {
    title: 'Contact BrandBattle | Get in Touch with Goldspade',
    description:
      'Have a question, feedback, partnership idea or issue with BrandBattle? Contact the Goldspade team.',
    url: `${SEO_CONFIG.domain}/contact`,
    siteName: 'Brand Battle',
    locale: 'en_IN',
    type: 'website',
  },
  twitter: {
    card: 'summary',
    title: 'Contact BrandBattle | Get in Touch with Goldspade',
    description:
      'Have a question, feedback, partnership idea or issue with BrandBattle? Contact the Goldspade team.',
    creator: '@GoldspadeFF',
  },
}

export default function ContactPage() {
  const breadcrumbs = buildBreadcrumbSchema([
    { name: 'Home', url: SEO_CONFIG.domain },
    { name: 'Contact', url: `${SEO_CONFIG.domain}/contact` },
  ])

  const contactJsonLd = {
    '@context': 'https://schema.org',
    '@type': 'ContactPage',
    name: 'Contact BrandBattle | Get in Touch with Goldspade',
    url: `${SEO_CONFIG.domain}/contact`,
    mainEntity: {
      '@type': 'Organization',
      name: 'Goldspade',
      alternateName: 'BrandBattle',
      url: SEO_CONFIG.domain,
      logo: SEO_CONFIG.organizationLogo,
      contactPoint: [
        {
          '@type': 'ContactPoint',
          email: 'hello@goldspade.in',
          telephone: '+91-8390612060',
          contactType: 'customer support and business inquiries',
          areaServed: 'IN',
          availableLanguage: ['English', 'Hindi'],
        },
      ],
      sameAs: [
        'https://x.com/GoldspadeFF',
      ],
    },
  }

  const combinedJsonLd = {
    '@context': 'https://schema.org',
    '@graph': [breadcrumbs, contactJsonLd],
  }

  return (
    <div className="min-h-screen bg-[#050505] text-white pt-32 pb-40">
      <StructuredDataScript jsonLd={combinedJsonLd} />
      <div className="w-full max-w-[1200px] mx-auto px-6 md:px-12">
        {/* Header Section */}
        <div className="max-w-3xl mb-16">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#f20ab0]/10 border border-[#f20ab0]/20 text-[#f20ab0] text-xs font-semibold uppercase tracking-[0.2em] mb-6">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Official Inquiries</span>
          </div>
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold font-[var(--font-display)] tracking-tight mb-6">
            Get in Touch.
          </h1>
          <p className="text-lg text-[#a1a1aa] leading-relaxed">
            Have a question, feedback, partnership idea or issue with BrandBattle? Contact the Goldspade team. We review every inquiry with care.
          </p>
        </div>

        {/* Contact Hierarchy Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 mb-16">
          {/* PRIMARY: General & Business Enquiries (Dominant / Featured Card) */}
          <div className="lg:col-span-7 p-8 sm:p-10 rounded-3xl bg-gradient-to-br from-[#0e0e12] to-[#070709] border border-[#f20ab0]/30 shadow-[0_0_40px_-20px_rgba(242,10,176,0.15)] flex flex-col justify-between relative overflow-hidden">
            <div className="absolute top-0 right-0 w-64 h-64 bg-[#f20ab0]/5 rounded-full blur-3xl pointer-events-none" />
            <div>
              <div className="flex items-center justify-between gap-4 mb-6">
                <div className="w-12 h-12 rounded-2xl bg-[#f20ab0]/15 border border-[#f20ab0]/30 flex items-center justify-center text-[#f20ab0]">
                  <Building2 className="w-6 h-6" />
                </div>
                <span className="text-[0.65rem] font-bold uppercase tracking-widest px-3 py-1 rounded-full bg-[#f20ab0]/20 text-[#f20ab0] border border-[#f20ab0]/40">
                  Primary Contact
                </span>
              </div>
              <h2 className="text-2xl sm:text-3xl font-bold font-[var(--font-display)] mb-3 text-white">
                General & Business Enquiries
              </h2>
              <p className="text-[#a1a1aa] text-sm sm:text-base leading-relaxed mb-8 max-w-xl">
                For commercial partnerships, brand verification, retail feed integration, enterprise API access, and general platform feedback.
              </p>
            </div>

            <div className="pt-6 border-t border-[#22222a]">
              <span className="text-xs uppercase tracking-wider text-[#71717a] block mb-2 font-medium">
                Official Business Email
              </span>
              <a
                href="mailto:hello@goldspade.in"
                className="group inline-flex items-center gap-3 text-lg sm:text-2xl font-bold text-white hover:text-[#f20ab0] transition-colors break-all focus:outline-none focus:ring-2 focus:ring-[#f20ab0] rounded-lg p-1 -m-1"
                aria-label="Send email for General and Business Enquiries to hello@goldspade.in"
              >
                <Mail className="w-5 h-5 text-[#f20ab0] shrink-0" />
                <span>hello@goldspade.in</span>
                <ArrowUpRight className="w-5 h-5 opacity-60 group-hover:opacity-100 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-all shrink-0" />
              </a>
            </div>
          </div>

          {/* Right Column: Secondary (Direct/Founder) + Phone */}
          <div className="lg:col-span-5 flex flex-col gap-8">
            {/* SECONDARY: Direct / Founder Contact */}
            <div className="p-8 rounded-3xl bg-[#0c0c0e] border border-[#1a1a20] hover:border-[#2a2a32] transition-colors flex-1 flex flex-col justify-between">
              <div>
                <div className="w-10 h-10 rounded-xl bg-white/5 border border-white/10 flex items-center justify-center text-white/80 mb-5">
                  <UserCheck className="w-5 h-5" />
                </div>
                <h2 className="text-xl font-bold font-[var(--font-display)] mb-2 text-white">
                  Direct / Founder Contact
                </h2>
                <p className="text-xs sm:text-sm text-[#71717a] leading-relaxed mb-6">
                  For critical escalations, direct technical collaboration, or strategic matters with the founding team.
                </p>
              </div>
              <div className="pt-4 border-t border-[#1a1a22]">
                <a
                  href="mailto:crohitpote17@gmail.com"
                  className="group inline-flex items-center gap-2.5 text-sm sm:text-base font-semibold text-white/90 hover:text-white transition-colors break-all focus:outline-none focus:ring-2 focus:ring-[#f20ab0] rounded-lg p-1 -m-1"
                  aria-label="Send email for Direct and Founder Contact to crohitpote17@gmail.com"
                >
                  <Mail className="w-4 h-4 text-[#a1a1aa] shrink-0" />
                  <span>crohitpote17@gmail.com</span>
                  <ArrowUpRight className="w-4 h-4 opacity-50 group-hover:opacity-100 transition-opacity shrink-0" />
                </a>
              </div>
            </div>

            {/* PHONE: Balanced & Clean */}
            <div className="p-8 rounded-3xl bg-[#0c0c0e] border border-[#1a1a20] hover:border-[#2a2a32] transition-colors">
              <div className="flex items-center gap-3 mb-3">
                <div className="w-10 h-10 rounded-xl bg-white/5 border border-white/10 flex items-center justify-center text-white/80 shrink-0">
                  <Phone className="w-5 h-5" />
                </div>
                <div>
                  <h2 className="text-base font-bold font-[var(--font-display)] text-white">
                    Phone Inquiries
                  </h2>
                  <span className="text-xs text-[#71717a]">Direct voice line for urgent queries</span>
                </div>
              </div>
              <div className="pt-3 border-t border-[#1a1a22] mt-4">
                <a
                  href="tel:+918390612060"
                  className="group inline-flex items-center gap-2.5 text-base sm:text-lg font-semibold text-white/90 hover:text-[#f20ab0] transition-colors focus:outline-none focus:ring-2 focus:ring-[#f20ab0] rounded-lg p-1 -m-1"
                  aria-label="Call Goldspade support at +91 8390612060"
                >
                  <span>+91 8390612060</span>
                  <ArrowUpRight className="w-4 h-4 opacity-50 group-hover:opacity-100 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-all" />
                </a>
              </div>
            </div>
          </div>
        </div>

        {/* SOCIAL & COMMUNITY: Follow Goldspade on X */}
        <div className="p-8 sm:p-10 rounded-3xl bg-[#0a0a0d] border border-[#1c1c24] flex flex-col sm:flex-row items-start sm:items-center justify-between gap-6 mb-16">
          <div className="flex items-start sm:items-center gap-5">
            <div className="w-12 h-12 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center text-white shrink-0">
              {/* Minimal SVG X Logo */}
              <svg className="w-5 h-5 fill-current" viewBox="0 0 24 24" aria-hidden="true">
                <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
              </svg>
            </div>
            <div>
              <div className="flex items-center gap-2 mb-1">
                <h2 className="text-lg font-bold text-white font-[var(--font-display)]">
                  Follow Goldspade
                </h2>
                <span className="text-xs text-[#71717a]">on X (formerly Twitter)</span>
              </div>
              <p className="text-sm text-[#8e8e93]">
                Real-time price intelligence updates, platform announcements, and verification alerts.
              </p>
            </div>
          </div>

          <a
            href="https://x.com/GoldspadeFF"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2.5 px-6 py-3 rounded-full bg-white text-black text-sm font-semibold hover:bg-[#e4e4e7] transition-all shrink-0 focus:outline-none focus:ring-2 focus:ring-white"
            aria-label="Visit Goldspade profile on X @GoldspadeFF"
          >
            <span>@GoldspadeFF</span>
            <ArrowUpRight className="w-4 h-4" />
          </a>
        </div>

        {/* Rapid Price Anomaly Reporting Helper Banner */}
        <div className="p-6 sm:p-8 rounded-2xl bg-[#0d0d10] border border-[#1f1f28] flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="w-10 h-10 rounded-xl bg-[#f20ab0]/10 flex items-center justify-center text-[#f20ab0] shrink-0">
              <ShieldAlert className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-white mb-0.5">
                Reporting a Price Anomaly or Suspicious Deal?
              </h3>
              <p className="text-xs text-[#71717a]">
                Send the product URL and observed price to{' '}
                <a
                  href="mailto:hello@goldspade.in?subject=Price%20Anomaly%20Report"
                  className="text-[#f20ab0] hover:underline"
                  aria-label="Email price anomaly report to hello@goldspade.in"
                >
                  hello@goldspade.in
                </a>
                . Our automated verification pipeline reviews quarantined anomalies in real time.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

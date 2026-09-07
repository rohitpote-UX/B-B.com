import React from 'react'
import type { Metadata } from 'next'
import { Mail, ShieldCheck, HelpCircle, MessageSquare } from 'lucide-react'
import StructuredDataScript from '@/seo/structuredData'
import { SEO_CONFIG, buildBreadcrumbSchema } from '@/lib/seo'

export const metadata: Metadata = {
  title: 'Contact BrandBattle — Trust Support & Merchant Enquiries',
  description:
    'Contact the BrandBattle engineering and trust verification team. Report incorrect prices, submit merchant inquiries, or request technical support.',
  alternates: {
    canonical: `${SEO_CONFIG.domain}/contact`,
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
    name: 'Contact BrandBattle',
    url: `${SEO_CONFIG.domain}/contact`,
    mainEntity: {
      '@type': 'Organization',
      name: SEO_CONFIG.organizationName,
      url: SEO_CONFIG.domain,
      contactPoint: {
        '@type': 'ContactPoint',
        email: SEO_CONFIG.supportEmail,
        contactType: 'customer support',
        areaServed: 'IN',
        availableLanguage: ['en', 'hi'],
      },
    },
  }

  const combinedJsonLd = {
    '@context': 'https://schema.org',
    '@graph': [breadcrumbs, contactJsonLd],
  }

  const channels = [
    {
      icon: ShieldCheck,
      title: 'Report a Price Anomaly',
      email: 'trust@brandbattle.in',
      desc: 'Spot an expired deal, broken image, or inaccurate price? Our verification team investigates within 2 hours.',
    },
    {
      icon: MessageSquare,
      title: 'Merchant & Retailer Feeds',
      email: 'partners@brandbattle.in',
      desc: 'Authorized brands and registered e-commerce retailers seeking to connect direct inventory APIs.',
    },
    {
      icon: HelpCircle,
      title: 'General Support & Feedback',
      email: 'support@brandbattle.in',
      desc: 'Questions about our comparison algorithms, shopping advisor features, or account management.',
    },
  ]

  return (
    <div className="min-h-screen bg-[#050505] text-white pt-32 pb-40">
      <StructuredDataScript jsonLd={combinedJsonLd} />
      <div className="w-full max-w-[1200px] mx-auto px-6 md:px-12">
        <div className="max-w-3xl mb-20">
          <span className="text-[0.75rem] font-semibold uppercase tracking-[0.25em] text-[#f20ab0] block mb-4">
            Connect With Us
          </span>
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold font-[var(--font-display)] tracking-tight mb-6">
            Get in Touch.
          </h1>
          <p className="text-lg text-[#a1a1aa] leading-relaxed">
            BrandBattle operates on radical transparency. Whether you have feedback on price anomalies, want to partner, or need technical assistance, our team is here.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-20">
          {channels.map((ch, idx) => {
            const Icon = ch.icon
            return (
              <div
                key={idx}
                className="p-8 rounded-3xl bg-[#0c0c0e] border border-[#1a1a20] flex flex-col justify-between"
              >
                <div>
                  <div className="w-12 h-12 rounded-2xl bg-[#f20ab0]/10 flex items-center justify-center text-[#f20ab0] mb-6">
                    <Icon className="w-6 h-6" />
                  </div>
                  <h2 className="text-xl font-bold font-[var(--font-display)] mb-3">{ch.title}</h2>
                  <p className="text-sm text-[#71717a] leading-relaxed mb-6">{ch.desc}</p>
                </div>
                <a
                  href={`mailto:${ch.email}`}
                  className="inline-flex items-center gap-2 text-sm font-semibold text-[#f20ab0] hover:underline"
                >
                  <Mail className="w-4 h-4" />
                  <span>{ch.email}</span>
                </a>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}

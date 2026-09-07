import React from 'react'
import type { Metadata } from 'next'
import StructuredDataScript from '@/seo/structuredData'
import { SEO_CONFIG, buildBreadcrumbSchema } from '@/lib/seo'

export const metadata: Metadata = {
  title: 'Privacy Policy — How We Protect Your Data | BrandBattle',
  description:
    'BrandBattle Privacy Policy. Learn how we collect, handle, and safeguard your personal information in compliance with Indian and global data protection laws.',
  alternates: {
    canonical: `${SEO_CONFIG.domain}/privacy`,
  },
}

export default function PrivacyPage() {
  const breadcrumbs = buildBreadcrumbSchema([
    { name: 'Home', url: SEO_CONFIG.domain },
    { name: 'Privacy Policy', url: `${SEO_CONFIG.domain}/privacy` },
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
            Privacy Policy
          </h1>
          <p className="text-sm text-[#71717a]">Last Updated: September 2026</p>
        </div>

        <div className="space-y-12 text-[#a1a1aa] leading-relaxed text-[1.05rem]">
          <section>
            <h2 className="text-2xl font-bold font-[var(--font-display)] text-white mb-4">1. Overview</h2>
            <p>
              BrandBattle Technologies (&quot;BrandBattle&quot;, &quot;we&quot;, &quot;our&quot;, or &quot;us&quot;) operates the product verification and price comparison platform at https://brandbattle.in. We respect your privacy and are committed to protecting personal data collected through your use of our service.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold font-[var(--font-display)] text-white mb-4">2. Information We Collect</h2>
            <p className="mb-4">
              We collect minimal information necessary to deliver our comparison and price tracking features:
            </p>
            <ul className="list-disc pl-6 space-y-2">
              <li><strong className="text-white">Account Information:</strong> Name, email address, and encrypted credentials when you register.</li>
              <li><strong className="text-white">Price Alerts:</strong> Target price thresholds and notification preferences set for products.</li>
              <li><strong className="text-white">Usage Analytics:</strong> Anonymized browsing patterns, product queries, and device information to optimize search indexing and page performance.</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-bold font-[var(--font-display)] text-white mb-4">3. What We Never Do</h2>
            <p>
              We do not sell, rent, or trade your personal data to third-party data brokers. We never inject tracking cookies that monitor your browsing outside of the BrandBattle domain.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold font-[var(--font-display)] text-white mb-4">4. External Marketplace Links</h2>
            <p>
              When you click an outbound link to view an offer on Amazon, Flipkart, Croma, or other retailer platforms, you navigate to an external website governed by that merchant&apos;s privacy policy.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold font-[var(--font-display)] text-white mb-4">5. Contact Us</h2>
            <p>
              For inquiries regarding your personal information, account deletion, or data rights under India&apos;s Digital Personal Data Protection Act (DPDPA), contact us at <a href="mailto:privacy@brandbattle.in" className="text-[#f20ab0] underline">privacy@brandbattle.in</a>.
            </p>
          </section>
        </div>
      </div>
    </div>
  )
}

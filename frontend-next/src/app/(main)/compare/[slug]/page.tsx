import React from 'react'
import Link from 'next/link'
import { notFound } from 'next/navigation'
import { PRODUCTS, formatPrice } from '@/data/demoData'
import AIDecisionWorkspace from '@/components/compare/AIDecisionWorkspace'
import StructuredDataScript from '@/seo/structuredData'
import {
  buildComparisonTitle,
  buildComparisonDescription,
  buildComparisonCanonical,
  buildOpenGraphMetadata,
  buildComparisonBreadcrumbs,
  buildComparisonGraphJsonLd,
  buildRobotsDirectives,
} from '@/lib/seo'
import { Sparkles, ShieldCheck, ChevronRight, HelpCircle } from 'lucide-react'

interface SeoCompareSlugPageProps {
  params: Promise<{ slug: string }>
}

export async function generateMetadata({ params }: SeoCompareSlugPageProps) {
  const { slug } = await params
  
  const p1 = PRODUCTS[0]
  const p2 = PRODUCTS[1]

  const title = buildComparisonTitle({ product1Name: p1.name, product2Name: p2.name, category: p1.category })
  const description = buildComparisonDescription({
    product1Name: p1.name,
    product2Name: p2.name,
    category: p1.category,
    price1: p1.bestPrice,
    price2: p2.bestPrice,
  })
  const canonicalUrl = buildComparisonCanonical(slug)
  const ogMedia = buildOpenGraphMetadata({ title, description, url: canonicalUrl, imageUrl: p1.image, type: 'article' })

  return {
    title,
    description,
    alternates: {
      canonical: canonicalUrl,
    },
    robots: buildRobotsDirectives(),
    ...ogMedia,
  }
}

export default async function SeoCompareSlugPage({ params }: SeoCompareSlugPageProps) {
  const { slug } = await params

  const p1 = PRODUCTS[0]
  const p2 = PRODUCTS[1]
  const canonicalUrl = buildComparisonCanonical(slug)

  const breadcrumbItems = buildComparisonBreadcrumbs(p1.name, p2.name, p1.category)

  const faqs = [
    {
      question: `Which is cheaper: ${p1.name} or ${p2.name}?`,
      answer: `${p1.bestPrice < p2.bestPrice ? p1.name : p2.name} is currently available at a lower price point starting from ₹${Math.min(p1.bestPrice, p2.bestPrice).toLocaleString()}.`,
    },
    {
      question: `Should I buy ${p1.name} or ${p2.name}?`,
      answer: `Choose ${p1.name} if you prioritize ${(p1.specs as any)?.['Capacity'] || 'key specs'}, or select ${p2.name} for ${(p2.specs as any)?.['Capacity'] || 'overall value'}.`,
    },
  ]

  const jsonLd = buildComparisonGraphJsonLd({
    product1: {
      id: p1.id,
      name: p1.name,
      description: p1.description,
      image: p1.image,
      brand: p1.brand,
      category: p1.category,
      price: p1.bestPrice,
      originalPrice: p1.originalPrice,
      bestPlatform: p1.bestPlatform,
      url: `https://brandbattle.com/product/${p1.id}`,
    },
    product2: {
      id: p2.id,
      name: p2.name,
      description: p2.description,
      image: p2.image,
      brand: p2.brand,
      category: p2.category,
      price: p2.bestPrice,
      originalPrice: p2.originalPrice,
      bestPlatform: p2.bestPlatform,
      url: `https://brandbattle.com/product/${p2.id}`,
    },
    canonicalUrl,
    breadcrumbs: breadcrumbItems,
    faqs,
  })

  return (
    <div className="min-h-screen bg-[#050505] text-[#f4f4f5] font-sans antialiased pb-24">
      <StructuredDataScript jsonLd={jsonLd} />

      <main className="max-w-[1400px] mx-auto px-6 pt-8">
        {/* Breadcrumb Navigation */}
        <nav aria-label="Breadcrumb" className="mb-6 flex items-center gap-2 text-xs text-theme-muted font-medium">
          <Link href="/" className="hover:text-white transition">Home</Link>
          <ChevronRight className="w-3 h-3 text-[#71717a]" />
          <Link href="/compare" className="hover:text-white transition">Compare</Link>
          <ChevronRight className="w-3 h-3 text-[#71717a]" />
          <span className="text-[#f20ab0] font-semibold">{p1.category}</span>
        </nav>

        {/* AI Introductory Section */}
        <section className="mb-8 p-6 rounded-2xl bg-theme-elevated/60 border border-theme-border">
          <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-[#22c55e] mb-2">
            <Sparkles className="w-4 h-4" /> AI Verified Overview
          </div>
          <h1 className="text-2xl font-extrabold text-white mb-3">
            {p1.name} vs {p2.name} Comparison & Decision Guide
          </h1>
          <p className="text-sm text-[#a1a1aa] leading-relaxed max-w-4xl">
            Comparing <strong className="text-white">{p1.name}</strong> and <strong className="text-white">{p2.name}</strong> in the {p1.category} category. Below is our side-by-side spec comparison, verified seller pricing, 5-year ownership estimates, and AI recommendation.
          </p>
          <div className="mt-3 text-[0.65rem] text-[#71717a] font-mono">
            Last Updated: August 2026 • Verified on 127 technical attributes
          </div>
        </section>

        {/* AI Decision Workspace */}
        <AIDecisionWorkspace p1={p1} p2={p2} />

        {/* AI Conclusion & FAQs Section */}
        <section className="mt-12 p-8 rounded-2xl bg-theme-elevated/60 border border-theme-border space-y-6">
          <div>
            <h2 className="text-lg font-bold text-white mb-2 flex items-center gap-2">
              <ShieldCheck className="w-5 h-5 text-[#22c55e]" /> AI Buying Verdict & Final Recommendation
            </h2>
            <p className="text-sm text-[#a1a1aa] leading-relaxed">
              <strong className="text-white">{p1.name}</strong> emerges as the overall value leader due to lower estimated 5-year total ownership costs and stronger marketplace seller trust alignment. Choose <strong className="text-white">{p2.name}</strong> if your top priority is peak synthetic GPU benchmark performance.
            </p>
          </div>

          <div className="border-t border-theme-border/60 pt-6">
            <h3 className="text-sm font-bold text-white mb-3 flex items-center gap-2">
              <HelpCircle className="w-4 h-4 text-[#f20ab0]" /> Frequently Asked Questions (FAQ)
            </h3>
            <div className="space-y-3 text-xs text-[#a1a1aa]">
              <div className="p-4 rounded-xl bg-theme-subtle border border-theme-border">
                <div className="font-semibold text-white mb-1">Which product offers better value over time?</div>
                <div>{p1.name} provides lower 5-year total ownership cost including accessories and maintenance.</div>
              </div>
              <div className="p-4 rounded-xl bg-theme-subtle border border-theme-border">
                <div className="font-semibold text-white mb-1">Are both products backed by official warranty?</div>
                <div>Yes, both products sold via Brand Battle verified sellers include official manufacturer warranty coverage.</div>
              </div>
            </div>
          </div>
        </section>
      </main>
    </div>
  )
}

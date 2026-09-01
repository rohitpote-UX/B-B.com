import React from 'react'
import Link from 'next/link'
import { Metadata } from 'next'
import { notFound } from 'next/navigation'
import AIDecisionWorkspace from '@/components/compare/AIDecisionWorkspace'
import StructuredDataScript from '@/seo/structuredData'
import {
  buildComparisonTitle,
  buildComparisonDescription,
  buildComparisonCanonical,
  buildOpenGraphMetadata,
  buildComparisonBreadcrumbItems,
  buildComparisonSchema,
  buildRobotsDirectives,
  resolveComparisonSlug,
  generateComparisonKeywords,
  buildComparisonAeoVerdict,
  SEO_CONFIG,
} from '@/lib/seo'
import { Sparkles, ShieldCheck, ChevronRight, HelpCircle } from 'lucide-react'

interface SeoCompareSlugPageProps {
  params: Promise<{ slug: string }>
}

export async function generateMetadata({ params }: SeoCompareSlugPageProps): Promise<Metadata> {
  const { slug } = await params
  const resolved = resolveComparisonSlug(slug)

  if (!resolved) {
    return {
      title: `Comparison Not Found | ${SEO_CONFIG.siteName}`,
      robots: { index: false, follow: false },
    }
  }

  const { p1, p2, canonicalSlug } = resolved
  const title = buildComparisonTitle({ product1Name: p1.name, product2Name: p2.name, category: p1.category })
  const description = buildComparisonDescription({
    product1Name: p1.name,
    product2Name: p2.name,
    category: p1.category,
    price1: p1.bestPrice,
    price2: p2.bestPrice,
    winnerName: p1.dealScore > p2.dealScore ? p1.name : p2.name,
  })
  const canonicalUrl = buildComparisonCanonical(canonicalSlug)
  const keywords = generateComparisonKeywords({
    product1Name: p1.name,
    product2Name: p2.name,
    category: p1.category,
  })
  const ogMedia = buildOpenGraphMetadata({
    title,
    description,
    url: canonicalUrl,
    imageUrl: p1.image,
    type: 'article',
  })

  return {
    title,
    description,
    keywords,
    alternates: {
      canonical: canonicalUrl,
    },
    robots: buildRobotsDirectives(),
    ...ogMedia,
  }
}

export default async function SeoCompareSlugPage({ params }: SeoCompareSlugPageProps) {
  const { slug } = await params
  const resolved = resolveComparisonSlug(slug)

  if (!resolved) {
    notFound()
  }

  const { p1, p2, canonicalSlug } = resolved
  const canonicalUrl = buildComparisonCanonical(canonicalSlug)
  const breadcrumbItems = buildComparisonBreadcrumbItems(p1.name, p2.name, p1.category)

  const cheaperProduct = p1.bestPrice < p2.bestPrice ? p1 : p2
  const winnerProduct = p1.dealScore >= p2.dealScore ? p1 : p2

  const faqs = [
    {
      question: `Which is cheaper: ${p1.name} or ${p2.name}?`,
      answer: `${cheaperProduct.name} is currently available at a lower price point starting from ₹${cheaperProduct.bestPrice.toLocaleString()} compared to ₹${(cheaperProduct.id === p1.id ? p2.bestPrice : p1.bestPrice).toLocaleString()}.`,
    },
    {
      question: `Should I buy ${p1.name} or ${p2.name}?`,
      answer: `Our AI consensus recommends ${winnerProduct.name} (Deal Score: ${winnerProduct.dealScore}/100) for overall value, verified specifications, and long-term ownership cost.`,
    },
    {
      question: `Are both ${p1.name} and ${p2.name} covered under official warranty?`,
      answer: `Yes, all verified offers compared on Brand Battle originate from authorized sellers providing official manufacturer warranty.`,
    },
  ]

  const aeoVerdict = buildComparisonAeoVerdict({
    p1Name: p1.name,
    p2Name: p2.name,
    p1Price: p1.bestPrice,
    p2Price: p2.bestPrice,
    category: p1.category,
    winnerName: winnerProduct.name,
    winnerReason: `${winnerProduct.name} achieved higher deal confidence (${winnerProduct.dealScore}/100) and verified satisfaction ratings.`,
  })

  const jsonLd = buildComparisonSchema({
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
      rating: p1.rating,
      totalReviews: p1.totalReviews,
      url: `${SEO_CONFIG.domain}/product/${p1.id}`,
      specs: p1.specs as unknown as Record<string, string | number>,
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
      rating: p2.rating,
      totalReviews: p2.totalReviews,
      url: `${SEO_CONFIG.domain}/product/${p2.id}`,
      specs: p2.specs as unknown as Record<string, string | number>,
    },
    canonicalUrl,
    breadcrumbs: breadcrumbItems,
    faqs,
  })

  return (
    <div className="min-h-screen bg-[#050505] text-[#f4f4f5] font-sans antialiased pb-24">
      <StructuredDataScript jsonLd={jsonLd} />

      {/* Semantic AEO / GEO Section for AI Crawlers */}
      <section aria-label="AI Comparison Summary" className="sr-only">
        <h2>{p1.name} vs {p2.name} — AI Verification Verdict</h2>
        <p>{aeoVerdict.directAnswer}</p>
        <ul>
          {aeoVerdict.supportingFacts.map((fact, i) => (
            <li key={i}>{fact}</li>
          ))}
        </ul>
      </section>

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
            Last Updated: September 2026 • Verified on technical specifications and real marketplace pricing
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
              <strong className="text-white">{winnerProduct.name}</strong> emerges as the overall value leader due to balanced specifications, verified pricing, and high confidence deal scoring. Choose <strong className="text-white">{winnerProduct.id === p1.id ? p2.name : p1.name}</strong> if you require specific alternative hardware capabilities.
            </p>
          </div>

          <div className="border-t border-theme-border/60 pt-6">
            <h3 className="text-sm font-bold text-white mb-3 flex items-center gap-2">
              <HelpCircle className="w-4 h-4 text-[#f20ab0]" /> Frequently Asked Questions (FAQ)
            </h3>
            <div className="space-y-3 text-xs text-[#a1a1aa]">
              {faqs.map((faq, idx) => (
                <div key={idx} className="p-4 rounded-xl bg-theme-subtle border border-theme-border">
                  <div className="font-semibold text-white mb-1">{faq.question}</div>
                  <div>{faq.answer}</div>
                </div>
              ))}
            </div>
          </div>
        </section>
      </main>
    </div>
  )
}

import React from 'react'
import type { Metadata } from 'next'
import { notFound } from 'next/navigation'
import Link from 'next/link'
import { ArrowLeft, Tag, ShieldCheck, TrendingDown } from 'lucide-react'
import StructuredDataScript from '@/seo/structuredData'
import { SEO_CONFIG, buildBreadcrumbSchema } from '@/lib/seo'
import { PRODUCTS, DEALS, PLATFORMS, formatPrice } from '@/data/demoData'
import { Deal } from '@/types'

interface DealCategoryPageProps {
  params: Promise<{ category: string }>
}

// Canonical category & festival mapping
const KNOWN_SLUGS: Record<string, { name: string; isFestival?: boolean; filterKey: string }> = {
  smartphones: { name: 'Smartphones', filterKey: 'smartphones' },
  laptops: { name: 'Laptops', filterKey: 'laptops' },
  headphones: { name: 'Headphones', filterKey: 'headphones' },
  televisions: { name: 'Televisions', filterKey: 'televisions' },
  tablets: { name: 'Tablets', filterKey: 'tablets' },
  cameras: { name: 'Cameras', filterKey: 'cameras' },
  gaming: { name: 'Gaming', filterKey: 'gaming' },
  audio: { name: 'Audio & Speakers', filterKey: 'speakers' },
  watches: { name: 'Smartwatches', filterKey: 'watches' },
  diwali: { name: 'Diwali Mega Sale Deals', isFestival: true, filterKey: 'all' },
  'great-indian-festival': { name: 'Great Indian Festival Deals', isFestival: true, filterKey: 'all' },
  'big-billion-days': { name: 'Big Billion Days Deals', isFestival: true, filterKey: 'all' },
  'black-friday': { name: 'Black Friday Deals', isFestival: true, filterKey: 'all' },
}

export async function generateStaticParams() {
  return Object.keys(KNOWN_SLUGS).map(slug => ({ category: slug }))
}

export async function generateMetadata({ params }: DealCategoryPageProps): Promise<Metadata> {
  const { category } = await params
  const catInfo = KNOWN_SLUGS[category.toLowerCase()]

  if (!catInfo) {
    return {
      title: `Deals Not Found | ${SEO_CONFIG.siteName}`,
      robots: { index: false, follow: false },
    }
  }

  const title = `${catInfo.name} Deals & Price Drops in India — BrandBattle`
  const description = `Verified ${catInfo.name} discounts across Amazon, Flipkart, Croma, and Reliance Digital. Algorithmic deal scores with 40% anomaly quarantine. Zero fake discounts.`
  const canonicalUrl = `${SEO_CONFIG.domain}/deals/${category.toLowerCase()}`

  return {
    title,
    description,
    alternates: {
      canonical: canonicalUrl,
    },
    openGraph: {
      title,
      description,
      url: canonicalUrl,
      type: 'website',
      siteName: SEO_CONFIG.siteName,
    },
  }
}

export default async function DealCategoryPage({ params }: DealCategoryPageProps) {
  const { category } = await params
  const catKey = category.toLowerCase()
  const catInfo = KNOWN_SLUGS[catKey]

  if (!catInfo) {
    notFound()
  }

  const breadcrumbs = buildBreadcrumbSchema([
    { name: 'Home', url: SEO_CONFIG.domain },
    { name: 'Deals', url: `${SEO_CONFIG.domain}/deals` },
    { name: catInfo.name, url: `${SEO_CONFIG.domain}/deals/${catKey}` },
  ])

  const collectionJsonLd = {
    '@context': 'https://schema.org',
    '@type': 'CollectionPage',
    name: `${catInfo.name} Deals & Discounts`,
    description: `Verified ${catInfo.name} deals from Amazon, Flipkart, Croma, and more.`,
    url: `${SEO_CONFIG.domain}/deals/${catKey}`,
  }

  const combinedJsonLd = {
    '@context': 'https://schema.org',
    '@graph': [breadcrumbs, collectionJsonLd],
  }

  // Filter deals by category or return top festival deals
  const dealsList = (DEALS as unknown as Deal[]).filter(d => {
    if (catInfo.isFestival) return d.dealScore >= 80
    const prodCat = (d.product?.category || '').toLowerCase()
    return prodCat.includes(catInfo.filterKey) || catInfo.filterKey.includes(prodCat)
  })

  return (
    <div className="min-h-screen bg-[#050505] text-white pt-32 pb-40">
      <StructuredDataScript jsonLd={combinedJsonLd} />
      <div className="w-full max-w-[1536px] mx-auto px-6 md:px-12">
        {/* Navigation Breadcrumb */}
        <div className="mb-12">
          <Link
            href="/deals"
            className="inline-flex items-center gap-2 text-xs font-semibold uppercase tracking-widest text-[#71717a] hover:text-[#f20ab0] transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>All Verified Deals</span>
          </Link>
        </div>

        {/* Hero Section */}
        <div className="max-w-4xl mb-16">
          <div className="flex items-center gap-3 mb-4">
            <span className="px-3 py-1 rounded-full bg-[#f20ab0]/10 border border-[#f20ab0]/20 text-[#f20ab0] text-xs font-semibold uppercase tracking-widest">
              {catInfo.isFestival ? 'Festival Event' : 'Category Deals'}
            </span>
            <span className="text-xs text-[#71717a]">
              {dealsList.length} Verified Drops
            </span>
          </div>
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold font-[var(--font-display)] tracking-tight mb-6">
            {catInfo.name}.
          </h1>
          <p className="text-lg text-[#a1a1aa] leading-relaxed">
            Algorithmic price drop detection cutting through artificial festival markups. Every listed deal is verified against historical baselines.
          </p>
        </div>

        {/* Deals Table */}
        <div className="space-y-4">
          <div className="hidden md:grid grid-cols-12 gap-8 text-xs font-semibold uppercase tracking-widest text-[#71717a] border-b border-[#1a1a20] pb-4 px-6">
            <div className="col-span-6">Product & Model</div>
            <div className="col-span-2">Platform</div>
            <div className="col-span-2 text-right">Deal Score</div>
            <div className="col-span-2 text-right">Best Price</div>
          </div>

          {dealsList.map(deal => (
            <Link
              key={deal.id}
              href={`/product/${deal.product.id}`}
              className="grid grid-cols-1 md:grid-cols-12 gap-4 md:gap-8 items-center p-6 rounded-2xl bg-[#0c0c0e] border border-[#1a1a20] hover:border-[#f20ab0]/40 transition-all group"
            >
              <div className="col-span-6 flex items-center gap-4">
                <img
                  src={deal.product.image}
                  alt={deal.product.name}
                  className="w-16 h-16 object-contain rounded-xl bg-black/40 p-2"
                />
                <div>
                  <span className="text-xs uppercase tracking-widest text-[#71717a] block mb-1">
                    {deal.product.brand}
                  </span>
                  <h2 className="text-base font-semibold text-white group-hover:text-[#f20ab0] transition-colors line-clamp-1">
                    {deal.product.name}
                  </h2>
                </div>
              </div>

              <div className="col-span-2 flex items-center gap-2">
                <span className="text-xs font-semibold uppercase tracking-wider text-white">
                  {(PLATFORMS as any)[deal.platform]?.name || deal.platform}
                </span>
              </div>

              <div className="col-span-2 md:text-right">
                <span className="inline-flex items-center gap-1 text-xs font-bold px-2.5 py-1 rounded-full bg-[#10b981]/10 text-[#10b981] border border-[#10b981]/20">
                  <ShieldCheck className="w-3.5 h-3.5" />
                  <span>{deal.dealScore}/100</span>
                </span>
              </div>

              <div className="col-span-2 md:text-right">
                <div className="text-base font-bold text-white">
                  {formatPrice(deal.product.bestPrice)}
                </div>
                <div className="text-xs text-[#71717a] line-through">
                  {formatPrice(deal.product.originalPrice)}
                </div>
              </div>
            </Link>
          ))}
        </div>
      </div>
    </div>
  )
}

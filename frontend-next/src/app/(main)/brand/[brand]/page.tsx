import React from 'react'
import type { Metadata } from 'next'
import { notFound } from 'next/navigation'
import Link from 'next/link'
import { ChevronRight, ShieldCheck, Tag, Sparkles, Scale, ExternalLink } from 'lucide-react'
import { PRODUCTS, formatPrice } from '@/data/demoData'
import BrandCatalogClient, { BrandProductItem } from '@/components/brand/BrandCatalogClient'
import StructuredDataScript from '@/seo/structuredData'
import {
  buildBrandTitle,
  buildBrandDescription,
  buildBrandCanonical,
  buildBrandBreadcrumbs,
  buildBreadcrumbSchema,
  buildRobotsDirectives,
  buildOpenGraphMetadata,
  buildComparisonSlug,
  SEO_CONFIG,
} from '@/lib/seo'

interface BrandPageProps {
  params: Promise<{ brand: string }>
}

// Canonical display names for known top brands
const CANONICAL_BRAND_NAMES: Record<string, string> = {
  apple: 'Apple',
  samsung: 'Samsung',
  google: 'Google',
  oneplus: 'OnePlus',
  xiaomi: 'Xiaomi',
  motorola: 'Motorola',
  sony: 'Sony',
  nothing: 'Nothing',
  vivo: 'Vivo',
  oppo: 'OPPO',
  realme: 'Realme',
  iqoo: 'iQOO',
  dell: 'Dell',
  hp: 'HP',
  asus: 'ASUS',
  boat: 'boAt',
  bose: 'Bose',
  jbl: 'JBL',
  nike: 'Nike',
  adidas: 'Adidas',
  puma: 'Puma',
  lg: 'LG',
}

// Helper to filter products cleanly for a given brand
function getBrandProducts(brandSlug: string) {
  const sLower = brandSlug.toLowerCase().trim()

  const products = PRODUCTS.filter(p => {
    const b = (p.brand || '').toLowerCase().trim()
    const specB = (p.specs && (p.specs as any)['Brand Name'] ? String((p.specs as any)['Brand Name']).toLowerCase().trim() : '')
    
    // Prevent false positives from scraped power banks / accessories with mismatched brands
    if (specB && specB !== sLower && !specB.includes(sLower) && !sLower.includes(specB)) {
      return false
    }

    if (sLower === 'nothing') {
      return b === 'nothing' || b === 'cmf by nothing' || p.name.toLowerCase().includes('nothing')
    }

    return b === sLower || (p.name.toLowerCase().startsWith(sLower + ' '))
  })

  // Format canonical name
  const canonicalName = CANONICAL_BRAND_NAMES[sLower] ||
    (products.length > 0 && products[0].brand ? products[0].brand : brandSlug.charAt(0).toUpperCase() + brandSlug.slice(1))

  const categories = Array.from(new Set(products.map(p => p.category).filter(Boolean))) as string[]
  const prices = products.map(p => p.bestPrice).filter(p => p && p > 0)
  const minPrice = prices.length > 0 ? Math.min(...prices) : 0
  const maxPrice = prices.length > 0 ? Math.max(...prices) : 0

  return {
    canonicalName,
    products,
    categories,
    minPrice,
    maxPrice,
  }
}

// Pre-render static pages for top catalog brands
export async function generateStaticParams() {
  const brandSet = new Set<string>(Object.keys(CANONICAL_BRAND_NAMES))
  
  // Also collect any brands with at least 2 catalog products
  const counts: Record<string, number> = {}
  PRODUCTS.forEach(p => {
    if (p.brand) {
      const slug = p.brand.toLowerCase().trim()
      counts[slug] = (counts[slug] || 0) + 1
    }
  })
  
  Object.entries(counts).forEach(([slug, count]) => {
    if (count >= 2 && slug.length >= 2 && !slug.includes(' ')) {
      brandSet.add(slug)
    }
  })

  return Array.from(brandSet).map(brand => ({ brand }))
}

export async function generateMetadata({ params }: BrandPageProps): Promise<Metadata> {
  const { brand } = await params
  const { canonicalName, products, categories } = getBrandProducts(brand)

  if (products.length === 0) {
    return {
      title: `Brand Not Found | ${SEO_CONFIG.siteName}`,
      robots: { index: false, follow: false },
    }
  }

  const title = buildBrandTitle(canonicalName)
  const description = buildBrandDescription(canonicalName, products.length, categories)
  const canonicalUrl = buildBrandCanonical(brand)

  const ogMedia = buildOpenGraphMetadata({
    title,
    description,
    url: canonicalUrl,
    imageUrl: products[0]?.image || SEO_CONFIG.defaultOgImage,
    type: 'website',
  })

  return {
    title: {
      absolute: title,
    },
    description,
    alternates: {
      canonical: canonicalUrl,
    },
    robots: buildRobotsDirectives(),
    ...ogMedia,
  }
}

export default async function BrandPage({ params }: BrandPageProps) {
  const { brand } = await params
  const { canonicalName, products, categories, minPrice, maxPrice } = getBrandProducts(brand)

  if (products.length === 0) {
    notFound()
  }

  const canonicalUrl = buildBrandCanonical(brand)
  const breadcrumbItems = buildBrandBreadcrumbs(canonicalName)
  const breadcrumbJsonLd = buildBreadcrumbSchema(breadcrumbItems)

  // Find relevant comparisons for products of this brand
  const comparisons: Array<{ title: string; slug: string; p1Name: string; p2Name: string }> = []
  if (products.length >= 2) {
    // Top 2 internal brand products
    const p1 = products[0]
    const p2 = products[1]
    const slug = buildComparisonSlug(p1.name, p2.name)
    comparisons.push({
      title: `${p1.name} vs ${p2.name}`,
      slug,
      p1Name: p1.name,
      p2Name: p2.name,
    })
  }

  // Cross-brand comparison with another top product in the same category
  if (products.length > 0) {
    const mainProd = products[0]
    const crossCompetitor = PRODUCTS.find(
      p => (p.brand || '').toLowerCase() !== brand.toLowerCase() &&
           p.category === mainProd.category &&
           p.bestPrice > 0
    )
    if (crossCompetitor) {
      const slug = buildComparisonSlug(mainProd.name, crossCompetitor.name)
      comparisons.push({
        title: `${mainProd.name} vs ${crossCompetitor.name}`,
        slug,
        p1Name: mainProd.name,
        p2Name: crossCompetitor.name,
      })
    }
  }

  // Schema.org CollectionPage & Brand entity
  const collectionJsonLd = {
    '@context': 'https://schema.org',
    '@type': 'CollectionPage',
    '@id': `${canonicalUrl}#collection`,
    name: `${canonicalName} Products, Prices & Comparisons`,
    description: `Explore verified ${canonicalName} products, live marketplace prices, and comparisons on BrandBattle.`,
    url: canonicalUrl,
    about: {
      '@type': 'Brand',
      name: canonicalName,
      url: canonicalUrl,
    },
    mainEntity: {
      '@type': 'ItemList',
      numberOfItems: products.length,
      itemListElement: products.slice(0, 15).map((p, idx) => ({
        '@type': 'ListItem',
        position: idx + 1,
        name: p.name,
        url: `${SEO_CONFIG.domain}/product/${p.id}`,
        ...(p.bestPrice && p.bestPrice > 0 ? {
          offers: {
            '@type': 'Offer',
            price: p.bestPrice,
            priceCurrency: 'INR',
            availability: 'https://schema.org/InStock',
            url: `${SEO_CONFIG.domain}/product/${p.id}`,
          },
        } : {}),
      })),
    },
  }

  const combinedJsonLd = {
    '@context': 'https://schema.org',
    '@graph': [breadcrumbJsonLd, collectionJsonLd],
  }

  // Map products to client interface
  const clientProducts: BrandProductItem[] = products.map(p => ({
    id: p.id,
    name: p.name,
    category: p.category || 'General',
    brand: p.brand || canonicalName,
    image: p.image,
    bestPrice: p.bestPrice,
    originalPrice: p.originalPrice,
    bestPlatform: p.bestPlatform,
    dealScore: p.dealScore || 0,
    rating: p.rating,
    totalReviews: p.totalReviews,
    specs: p.specs as unknown as Record<string, string | number>,
  }))

  return (
    <div className="min-h-screen bg-[#050505] text-white pt-28 pb-40">
      <StructuredDataScript jsonLd={combinedJsonLd} />

      {/* Semantic Machine-Readable AEO/GEO Content for AI Crawlers */}
      <section aria-label="Brand Overview FactSheet" className="sr-only">
        <h2>{canonicalName} Products & Price Intelligence Summary</h2>
        <p>
          BrandBattle provides verified price intelligence and hardware specifications for {products.length} {canonicalName} products across {categories.join(', ')}.
          Observed price range starts from {formatPrice(minPrice)} to {formatPrice(maxPrice)}.
        </p>
        <ul>
          {products.slice(0, 10).map(p => (
            <li key={p.id}>
              {p.name} — Lowest verified price: {formatPrice(p.bestPrice)} on {p.bestPlatform || 'Amazon/Flipkart'}.
            </li>
          ))}
        </ul>
      </section>

      <div className="w-full max-w-[1536px] mx-auto px-6 sm:px-10 lg:px-16">
        {/* Breadcrumb Navigation */}
        <nav aria-label="Breadcrumb" className="mb-8 flex items-center gap-2 text-xs text-white/50 font-mono">
          <Link href="/" className="hover:text-white transition">Home</Link>
          <ChevronRight className="w-3.5 h-3.5 text-white/30" />
          <Link href="/#browse-by-brand" className="hover:text-white transition">Brands</Link>
          <ChevronRight className="w-3.5 h-3.5 text-white/30" />
          <span className="text-[#ff1695] font-semibold">{canonicalName}</span>
        </nav>

        {/* Hero Header */}
        <div className="flex flex-col lg:flex-row lg:items-end justify-between gap-8 mb-12 pb-10 border-b border-white/10">
          <div className="max-w-3xl">
            <div className="flex items-center gap-3 mb-4">
              <span className="px-3 py-1 rounded-full bg-[#ff1695]/10 border border-[#ff1695]/20 text-[#ff1695] text-xs font-mono font-semibold uppercase tracking-widest flex items-center gap-1.5">
                <Sparkles className="w-3.5 h-3.5" />
                <span>VERIFIED BRAND HUB</span>
              </span>
              <span className="text-xs text-white/50 font-mono">
                {products.length} {products.length === 1 ? 'Product' : 'Products'} Cataloged
              </span>
            </div>

            <h1 className="text-4xl sm:text-5xl md:text-6xl font-extrabold font-[var(--font-display)] tracking-tight uppercase mb-4">
              {canonicalName} <span className="text-[#ff1695] italic">Products & Prices.</span>
            </h1>

            <p className="text-sm sm:text-base text-white/70 leading-relaxed max-w-2xl font-light">
              Explore verified {canonicalName} hardware, track real marketplace price drops across Amazon and Flipkart, analyze specifications, and compare side-by-side before you buy.
            </p>

            {/* Category Badges */}
            <div className="flex flex-wrap items-center gap-2 mt-6">
              <span className="text-xs font-mono uppercase text-white/40 mr-1">Categories:</span>
              {categories.map(cat => (
                <Link
                  key={cat}
                  href={`/deals/${cat.toLowerCase().replace(/[^a-z0-9]+/g, '-')}`}
                  className="px-3 py-1 rounded-lg bg-white/[0.03] hover:bg-white/[0.08] border border-white/10 text-xs font-mono text-white/80 hover:text-white transition"
                >
                  {cat}
                </Link>
              ))}
            </div>
          </div>

          {/* Quick Metrics Card */}
          <div className="grid grid-cols-2 gap-3 sm:gap-4 p-5 rounded-2xl bg-white/[0.02] border border-white/10 lg:w-80">
            <div>
              <span className="text-[0.68rem] uppercase font-mono tracking-widest text-white/40 block mb-1">
                Observed Low
              </span>
              <div className="text-xl sm:text-2xl font-bold text-white font-[var(--font-display)]">
                {formatPrice(minPrice)}
              </div>
            </div>
            <div>
              <span className="text-[0.68rem] uppercase font-mono tracking-widest text-white/40 block mb-1">
                Observed High
              </span>
              <div className="text-xl sm:text-2xl font-bold text-white font-[var(--font-display)]">
                {formatPrice(maxPrice)}
              </div>
            </div>
            <div className="col-span-2 pt-3 border-t border-white/[0.06] flex items-center justify-between text-xs text-white/50 font-mono">
              <span>Stores Verified</span>
              <span className="text-[#10b981] flex items-center gap-1 font-semibold">
                <ShieldCheck className="w-3.5 h-3.5" /> Amazon + Flipkart
              </span>
            </div>
          </div>
        </div>

        {/* Interactive Client Catalog (Filter by category, sort by price/score) */}
        <section aria-labelledby="brand-catalog-heading" className="mb-16">
          <h2 id="brand-catalog-heading" className="sr-only">
            {canonicalName} Product Catalog
          </h2>
          <BrandCatalogClient
            brandName={canonicalName}
            products={clientProducts}
            categories={categories}
          />
        </section>

        {/* Head-to-Head Comparisons Section */}
        {comparisons.length > 0 && (
          <section className="mb-16 p-8 rounded-3xl bg-white/[0.02] border border-white/10">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
              <div>
                <div className="flex items-center gap-2 text-xs font-mono uppercase tracking-widest text-[#ff1695] font-semibold mb-1">
                  <Scale className="w-4 h-4" />
                  <span>DECISION GUIDES</span>
                </div>
                <h2 className="text-2xl font-bold text-white font-[var(--font-display)] uppercase">
                  Top {canonicalName} <span className="text-[#ff1695]">Comparisons.</span>
                </h2>
              </div>
              <Link
                href="/compare"
                className="inline-flex items-center gap-1.5 text-xs font-mono uppercase tracking-wider text-white/60 hover:text-white transition"
              >
                <span>Launch Compare Workspace</span>
                <ChevronRight className="w-3.5 h-3.5 text-[#ff1695]" />
              </Link>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {comparisons.map((comp, idx) => (
                <Link
                  key={idx}
                  href={`/compare/${comp.slug}`}
                  className="group flex items-center justify-between p-5 rounded-2xl bg-white/[0.02] hover:bg-white/[0.05] border border-white/10 hover:border-[#ff1695]/40 transition-all duration-300"
                >
                  <div>
                    <span className="text-xs text-[#ff1695] font-mono block mb-1">Head-to-Head</span>
                    <h3 className="text-base font-semibold text-white group-hover:text-[#ff1695] transition-colors">
                      {comp.title}
                    </h3>
                  </div>
                  <span className="p-2 rounded-xl bg-white/[0.04] group-hover:bg-[#ff1695] text-white/60 group-hover:text-white transition-all">
                    <ChevronRight className="w-4 h-4" />
                  </span>
                </Link>
              ))}
            </div>
          </section>
        )}

        {/* SEO Contextual Internal Links Section */}
        <section className="p-8 rounded-2xl bg-white/[0.01] border border-white/[0.08] text-xs text-white/50 space-y-4">
          <h3 className="text-sm font-semibold text-white uppercase tracking-wider font-mono">
            Explore {canonicalName} on BrandBattle
          </h3>
          <p className="leading-relaxed">
            BrandBattle aggregates live product specifications, historical price observations, and marketplace deals for {canonicalName} in India.
            All price points and retailer offers are verified against authorized sellers across Amazon India and Flipkart.
          </p>
          <div className="flex flex-wrap gap-4 pt-2 border-t border-white/[0.06] text-white/70 font-mono">
            <Link href="/" className="hover:text-white transition">Home</Link>
            <span>•</span>
            <Link href="/deals" className="hover:text-white transition">All Verified Deals</Link>
            <span>•</span>
            <Link href="/compare" className="hover:text-white transition">Product Comparisons</Link>
            <span>•</span>
            <Link href="/price-verification" className="hover:text-white transition">Price Verification Methodology</Link>
          </div>
        </section>
      </div>
    </div>
  )
}

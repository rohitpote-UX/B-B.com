import React from 'react'
import { Metadata } from 'next'
import { notFound } from 'next/navigation'
import { PRODUCTS } from '@/data/demoData'
import ProductDetailClient from '@/components/product/ProductDetailClient'
import StructuredDataScript from '@/seo/structuredData'
import {
  buildProductTitle,
  buildProductDescription,
  buildProductCanonical,
  buildRobotsDirectives,
  buildOpenGraphMetadata,
  generateProductKeywords,
  buildProductSchema,
  buildBreadcrumbSchema,
  buildProductBreadcrumbItems,
  buildGeoFactSheet,
  formatGeoFactSheetText,
  buildProductAeoAnswers,
  SEO_CONFIG,
} from '@/lib/seo'

interface ProductPageProps {
  params: Promise<{ id: string }>
}

export async function generateStaticParams() {
  return PRODUCTS.slice(0, 30).map(p => ({
    id: p.id.toString(),
  }))
}

export async function generateMetadata({ params }: ProductPageProps): Promise<Metadata> {
  const { id } = await params
  const product = PRODUCTS.find(p => p.id === parseInt(id))

  if (!product) {
    return {
      title: `Product Not Found | ${SEO_CONFIG.siteName}`,
      robots: { index: false, follow: false },
    }
  }

  const title = buildProductTitle({ name: product.name, brand: product.brand, category: product.category })
  const description = buildProductDescription({
    name: product.name,
    brand: product.brand,
    category: product.category,
    price: product.bestPrice,
    specSnippet: (product.specs as any)?.['Processor'] || (product.specs as any)?.['Display'] || undefined,
    marketplaceCount: product.prices?.length || 1,
  })
  const canonicalUrl = buildProductCanonical(product.id)
  const keywords = generateProductKeywords({
    productName: product.name,
    brand: product.brand,
    category: product.category,
  })
  const ogMedia = buildOpenGraphMetadata({
    title,
    description,
    url: canonicalUrl,
    imageUrl: product.image,
    type: 'website',
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

export default async function ProductDetailPage({ params }: ProductPageProps) {
  const { id } = await params
  const product = PRODUCTS.find(p => p.id === parseInt(id))

  if (!product) {
    notFound()
  }

  const canonicalUrl = buildProductCanonical(product.id)
  const breadcrumbItems = buildProductBreadcrumbItems(product.category, product.brand, product.name)
  const breadcrumbJsonLd = buildBreadcrumbSchema(breadcrumbItems)

  const productJsonLd = buildProductSchema({
    id: product.id,
    name: product.name,
    description: product.description,
    image: product.image,
    brand: product.brand,
    category: product.category,
    price: product.bestPrice,
    originalPrice: product.originalPrice,
    bestPlatform: product.bestPlatform,
    rating: product.rating,
    totalReviews: product.totalReviews,
    url: canonicalUrl,
    specs: product.specs as unknown as Record<string, string | number>,
  })

  const geoFactSheet = buildGeoFactSheet({
    name: product.name,
    brand: product.brand,
    category: product.category,
    price: product.bestPrice,
    bestPlatform: product.bestPlatform,
    specs: product.specs as unknown as Record<string, string | number>,
    dealScore: product.dealScore,
    rating: product.rating,
    totalReviews: product.totalReviews,
  })

  const aeoAnswers = buildProductAeoAnswers({
    name: product.name,
    brand: product.brand,
    price: product.bestPrice,
    bestPlatform: product.bestPlatform,
    category: product.category,
    specs: product.specs as unknown as Record<string, string | number>,
  })

  const combinedJsonLd = {
    '@context': 'https://schema.org',
    '@graph': [
      productJsonLd,
      breadcrumbJsonLd,
      {
        '@type': 'FAQPage',
        mainEntity: aeoAnswers.map(ans => ({
          '@type': 'Question',
          name: ans.question,
          acceptedAnswer: {
            '@type': 'Answer',
            text: ans.directAnswer,
          },
        })),
      },
    ],
  }

  return (
    <>
      <StructuredDataScript jsonLd={combinedJsonLd} />

      {/* Semantic GEO & AEO machine-readable factsheet for AI search engines (Perplexity, ChatGPT, Claude, Gemini) */}
      <section aria-label="AI Verification Summary" className="sr-only">
        <h2>{product.name} — AI Verification & Specification Summary</h2>
        <p>{formatGeoFactSheetText(geoFactSheet)}</p>
        <div>
          {aeoAnswers.map((item, idx) => (
            <article key={idx}>
              <h3>{item.question}</h3>
              <p>{item.directAnswer}</p>
            </article>
          ))}
        </div>
      </section>

      {/* Render 100% untouched interactive client UI */}
      <ProductDetailClient initialId={id} />
    </>
  )
}

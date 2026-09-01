import { Metadata } from 'next'

export interface ComparisonSeoProps {
  product1Name: string
  product2Name: string
  categoryName: string
  canonicalSlug: string
  price1?: number
  price2?: number
  imageUrl?: string
}

export function buildComparisonMetadata({
  product1Name,
  product2Name,
  categoryName,
  canonicalSlug,
  price1 = 0,
  price2 = 0,
  imageUrl = 'https://brandbattle.com/og-compare.png',
}: ComparisonSeoProps): Metadata {
  const title = `${product1Name} vs ${product2Name} | AI Comparison, Price & Specs | Brand Battle`
  const description = `Compare ${product1Name} (₹${price1.toLocaleString()}) and ${product2Name} (₹${price2.toLocaleString()}) side-by-side in ${categoryName}. Verified specs, 5-year TCO, AI recommendations, and live deals.`
  const canonicalUrl = `https://brandbattle.com/compare/${canonicalSlug}`

  return {
    title,
    description,
    alternates: {
      canonical: canonicalUrl,
    },
    robots: {
      index: true,
      follow: true,
      'max-image-preview': 'large',
      'max-snippet': -1,
      'max-video-preview': -1,
    },
    openGraph: {
      title,
      description,
      url: canonicalUrl,
      siteName: 'Brand Battle',
      images: [
        {
          url: imageUrl,
          width: 1200,
          height: 630,
          alt: `${product1Name} vs ${product2Name}`,
        },
      ],
      type: 'article',
    },
    twitter: {
      card: 'summary_large_image',
      title,
      description,
      images: [imageUrl],
    },
  }
}

/**
 * Brand Battle — OpenGraph & Twitter Card Engine
 * Builds social sharing preview metadata for products, comparisons, categories, and site pages.
 */

import { Metadata } from 'next'
import { SEO_CONFIG } from './seo-config'

export interface OpenGraphProps {
  title: string
  description: string
  url: string
  imageUrl?: string
  type?: 'website' | 'article' | 'product'
}

export function buildOpenGraphMetadata({
  title,
  description,
  url,
  imageUrl,
  type = 'website',
}: OpenGraphProps): { openGraph: Metadata['openGraph']; twitter: Metadata['twitter'] } {
  const finalImage = imageUrl || SEO_CONFIG.defaultOgImage

  return {
    openGraph: {
      title,
      description,
      url,
      siteName: SEO_CONFIG.siteName,
      locale: SEO_CONFIG.locale,
      type: type as any,
      images: [
        {
          url: finalImage,
          width: 1200,
          height: 630,
          alt: title,
        },
      ],
    },
    twitter: {
      card: 'summary_large_image',
      title,
      description,
      site: SEO_CONFIG.twitterHandle,
      images: [finalImage],
    },
  }
}

import type { MetadataRoute } from 'next'
import { PRODUCTS } from '@/data/demoData'

export default function sitemap(): MetadataRoute.Sitemap {
  const appUrl = process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000'

  // Static routes
  const staticRoutes = [
    '',
    '/search',
    '/compare',
    '/deals',
    '/advisor',
    '/discover',
  ].map((route) => ({
    url: `${appUrl}${route}`,
    lastModified: new Date(),
    changeFrequency: 'daily' as const,
    priority: route === '' ? 1.0 : 0.8,
  }))

  // Dynamic product routes
  const productRoutes = PRODUCTS.map((p) => ({
    url: `${appUrl}/product/${p.id}`,
    lastModified: new Date(),
    changeFrequency: 'weekly' as const,
    priority: 0.6,
  }))

  return [...staticRoutes, ...productRoutes]
}

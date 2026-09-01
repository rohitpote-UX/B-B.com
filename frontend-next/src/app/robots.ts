import type { MetadataRoute } from 'next'
import { SEO_CONFIG } from '@/lib/seo/seo-config'

export default function robots(): MetadataRoute.Robots {
  const appUrl = SEO_CONFIG.domain

  return {
    rules: [
      {
        userAgent: '*',
        allow: ['/', '/product/', '/compare/', '/discover', '/deals'],
        disallow: [
          '/admin/',
          '/api/',
          '/profile',
          '/login',
          '/signup',
          '/*?*sort=*',
          '/*?*filter=*',
          '/*?*ref=*',
          '/*?*utm_*',
        ],
      },
      {
        userAgent: 'Googlebot',
        allow: ['/', '/product/', '/compare/', '/discover', '/deals'],
        disallow: ['/admin/', '/api/', '/profile', '/login', '/signup'],
      },
    ],
    sitemap: `${appUrl}/sitemap.xml`,
  }
}

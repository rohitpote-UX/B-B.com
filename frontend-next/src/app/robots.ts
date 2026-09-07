import type { MetadataRoute } from 'next'
import { SEO_CONFIG } from '@/lib/seo/seo-config'

export default function robots(): MetadataRoute.Robots {
  const appUrl = SEO_CONFIG.domain

  const publicAllowed = [
    '/',
    '/product/',
    '/compare/',
    '/discover',
    '/deals',
    '/manifesto',
    '/advisor',
    '/about',
    '/team',
    '/price-verification',
    '/privacy',
    '/terms',
    '/contact',
  ]

  return {
    rules: [
      {
        userAgent: '*',
        allow: publicAllowed,
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
          '/*?*color=*',
          '/*?*size=*',
        ],
      },
      {
        userAgent: 'Googlebot',
        allow: publicAllowed,
        disallow: ['/admin/', '/api/', '/profile', '/login', '/signup'],
      },
      {
        userAgent: 'Bingbot',
        allow: publicAllowed,
        disallow: ['/admin/', '/api/', '/profile', '/login', '/signup'],
      },
      {
        userAgent: 'GPTBot',
        allow: publicAllowed,
        disallow: ['/admin/', '/api/', '/profile', '/login', '/signup'],
      },
      {
        userAgent: 'PerplexityBot',
        allow: publicAllowed,
        disallow: ['/admin/', '/api/', '/profile', '/login', '/signup'],
      },
      {
        userAgent: 'ClaudeBot',
        allow: publicAllowed,
        disallow: ['/admin/', '/api/', '/profile', '/login', '/signup'],
      },
      {
        userAgent: 'Applebot',
        allow: publicAllowed,
        disallow: ['/admin/', '/api/', '/profile', '/login', '/signup'],
      },
    ],
    sitemap: `${appUrl}/sitemap.xml`,
  }
}

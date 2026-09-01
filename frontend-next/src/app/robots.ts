import type { MetadataRoute } from 'next'
import { SEO_CONFIG } from '@/lib/seo/seo-config'

export default function robots(): MetadataRoute.Robots {
  const appUrl = SEO_CONFIG.domain

  return {
    rules: [
      {
        userAgent: '*',
        allow: ['/', '/product/', '/compare/', '/discover', '/deals', '/manifesto', '/advisor'],
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
        allow: ['/', '/product/', '/compare/', '/discover', '/deals', '/manifesto', '/advisor'],
        disallow: ['/admin/', '/api/', '/profile', '/login', '/signup'],
      },
      {
        userAgent: 'Bingbot',
        allow: ['/', '/product/', '/compare/', '/discover', '/deals', '/manifesto', '/advisor'],
        disallow: ['/admin/', '/api/', '/profile', '/login', '/signup'],
      },
      {
        userAgent: 'GPTBot',
        allow: ['/', '/product/', '/compare/', '/discover', '/deals', '/manifesto', '/advisor'],
        disallow: ['/admin/', '/api/', '/profile', '/login', '/signup'],
      },
      {
        userAgent: 'PerplexityBot',
        allow: ['/', '/product/', '/compare/', '/discover', '/deals', '/manifesto', '/advisor'],
        disallow: ['/admin/', '/api/', '/profile', '/login', '/signup'],
      },
      {
        userAgent: 'ClaudeBot',
        allow: ['/', '/product/', '/compare/', '/discover', '/deals', '/manifesto', '/advisor'],
        disallow: ['/admin/', '/api/', '/profile', '/login', '/signup'],
      },
      {
        userAgent: 'Applebot',
        allow: ['/', '/product/', '/compare/', '/discover', '/deals', '/manifesto', '/advisor'],
        disallow: ['/admin/', '/api/', '/profile', '/login', '/signup'],
      },
    ],
    sitemap: `${appUrl}/sitemap.xml`,
  }
}

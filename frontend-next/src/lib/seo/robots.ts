/**
 * Brand Battle — Robots Directives Engine
 * Provides indexability rules for pages, faceted search URLs, and parameter combinations.
 */

import { Metadata } from 'next'

export interface RobotsOptions {
  isIndexable?: boolean
  noSnippets?: boolean
  maxImagePreview?: 'none' | 'standard' | 'large'
}

/**
 * Generates Next.js Robots metadata object.
 */
export function buildRobotsDirectives(options: RobotsOptions = {}): Metadata['robots'] {
  const isIndexable = options.isIndexable ?? true

  if (!isIndexable) {
    return {
      index: false,
      follow: true,
      nocache: true,
    }
  }

  return {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': options.maxImagePreview || 'large',
      'max-snippet': -1,
    },
  }
}

/**
 * Determines whether a given request query string should trigger noindex.
 * Protects against crawl parameter explosions (e.g. ?sort=price&color=red&page=3).
 */
export function shouldNoindexQuery(searchParams: Record<string, string | string[] | undefined>): boolean {
  if (!searchParams) return false

  const paramKeys = Object.keys(searchParams)
  if (paramKeys.length === 0) return false

  // Disallow indexation if tracking/filter parameters are present
  const noindexParams = ['sort', 'min_price', 'max_price', 'color', 'size', 'ref', 'gclid', 'page']
  return paramKeys.some(k => noindexParams.includes(k.toLowerCase()))
}

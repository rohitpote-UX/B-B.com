import { PRODUCTS } from '@/data/demoData'
import { Product } from '@/types'
import { FALLBACK_PRODUCT_IMAGE } from '@/lib/image-fallback'
import api from '@/lib/api'

export interface CatalogQueryOptions {
  query?: string
  category?: string
  brand?: string
  sortBy?: 'relevance' | 'price_asc' | 'price_desc' | 'rating' | 'newest' | 'deal_score' | string
  page?: number
  pageSize?: number
  minPrice?: number
  maxPrice?: number
}

export interface CatalogQueryResult {
  products: Product[]
  total: number
  page: number
  pageSize: number
  totalPages: number
  fromApi: boolean
}

/**
 * Standardizes an API product payload into BrandBattle's Product interface.
 */
export function adaptApiProduct(item: any): Product {
  const brandName = item.brand?.name || (typeof item.brand === 'string' ? item.brand : '')
  const categoryName = item.category?.name || (typeof item.category === 'string' ? item.category : 'General')
  const bestPrice = Number(item.current_best_price || item.bestPrice || item.lowest_price || 0)
  const originalPrice = Number(item.highest_price || item.originalPrice || bestPrice)

  return {
    id: Number(item.id),
    name: item.name || 'Unnamed Product',
    brand: brandName,
    category: categoryName,
    image: item.image_url || item.image || FALLBACK_PRODUCT_IMAGE,
    rating: Number(item.average_rating || item.rating || 0),
    totalReviews: Number(item.total_reviews || item.totalReviews || 0),
    bestPrice,
    originalPrice,
    bestPlatform: item.current_best_platform || item.bestPlatform || 'amazon',
    currency: item.currency || 'INR',
    dealScore: Number(item.deal_score || item.dealScore || 0),
    tags: Array.isArray(item.tags) ? item.tags : [],
    description: item.description || item.short_description || '',
    specs: item.specifications || item.specs || {},
    features: Array.isArray(item.features) ? item.features : [],
    prices: Array.isArray(item.prices) ? item.prices : [],
    productUrl: item.product_url || item.productUrl,
    flipkartUrl: item.flipkart_url || item.flipkartUrl,
    feedBadge: item.feedBadge,
  }
}

/**
 * Filters, sorts, and paginates the local catalog in memory.
 */
export function filterLocalCatalog(options: CatalogQueryOptions): CatalogQueryResult {
  const {
    query = '',
    category = 'all',
    brand = '',
    sortBy = 'relevance',
    page = 1,
    pageSize = 24,
    minPrice,
    maxPrice,
  } = options

  let list = (PRODUCTS as unknown as Product[])

  // Brand filter
  if (brand && brand !== 'all') {
    const bLower = brand.toLowerCase().trim()
    list = list.filter((p) => {
      const pBrand = (p.brand || '').toLowerCase().trim()
      if (bLower === 'nothing') {
        return pBrand === 'nothing' || pBrand === 'cmf by nothing'
      }
      return pBrand === bLower
    })
  }

  // Category filter
  if (category && category !== 'all') {
    const cLower = category.toLowerCase().trim()
    list = list.filter((p) => (p.category || '').toLowerCase().trim() === cLower)
  }

  // Query search (across name, brand, category, description, and specs)
  if (query && query.trim()) {
    const qLower = query.toLowerCase().trim()
    list = list.filter((p) => {
      const inName = (p.name || '').toLowerCase().includes(qLower)
      const inBrand = (p.brand || '').toLowerCase().includes(qLower)
      const inCategory = (p.category || '').toLowerCase().includes(qLower)
      const inDesc = (p.description || '').toLowerCase().includes(qLower)
      return inName || inBrand || inCategory || inDesc
    })
  }

  // Price range filters
  if (minPrice !== undefined && minPrice > 0) {
    list = list.filter((p) => p.bestPrice >= minPrice)
  }
  if (maxPrice !== undefined && maxPrice > 0) {
    list = list.filter((p) => p.bestPrice <= maxPrice)
  }

  // Sorting
  const sorted = [...list]
  switch (sortBy) {
    case 'price_asc':
      sorted.sort((a, b) => a.bestPrice - b.bestPrice)
      break
    case 'price_desc':
      sorted.sort((a, b) => b.bestPrice - a.bestPrice)
      break
    case 'rating':
      sorted.sort((a, b) => b.rating - a.rating)
      break
    case 'deal_score':
      sorted.sort((a, b) => (b.dealScore || 0) - (a.dealScore || 0))
      break
    case 'newest':
      // Stable reverse ID / new launch priority
      sorted.sort((a, b) => b.id - a.id)
      break
    case 'relevance':
    default:
      // Relevance prefers high deal scores and ratings
      sorted.sort((a, b) => (b.dealScore * 0.6 + b.rating * 10) - (a.dealScore * 0.6 + a.rating * 10))
      break
  }

  const total = sorted.length
  const totalPages = Math.max(1, Math.ceil(total / pageSize))
  const safePage = Math.max(1, Math.min(page, totalPages))
  const offset = (safePage - 1) * pageSize
  const paginated = sorted.slice(offset, offset + pageSize)

  return {
    products: paginated,
    total,
    page: safePage,
    pageSize,
    totalPages,
    fromApi: false,
  }
}

/**
 * Searches the full catalog. Tries the backend API with a fast timeout,
 * and seamlessly falls back to the rich local catalog if the backend is cold/offline.
 */
export async function searchCatalog(options: CatalogQueryOptions): Promise<CatalogQueryResult> {
  const {
    query = '',
    category = 'all',
    brand = '',
    sortBy = 'relevance',
    page = 1,
    pageSize = 24,
  } = options

  // Attempt backend API fetch
  try {
    const params: Record<string, any> = {
      page,
      page_size: pageSize,
      sort_by: sortBy,
    }
    if (query && query.trim()) params.query = query.trim()
    if (category && category !== 'all') params.category = category.trim()
    if (brand && brand !== 'all') params.brand = brand.trim()

    // Use a 3.5s timeout for fast responsiveness
    const response = await Promise.race([
      api.products.list(params),
      new Promise<never>((_, reject) =>
        setTimeout(() => reject(new Error('Catalog API Timeout')), 3500)
      ),
    ])

    if (response?.data?.products && Array.isArray(response.data.products) && response.data.total > 0) {
      const adaptedProducts = response.data.products.map(adaptApiProduct)
      return {
        products: adaptedProducts,
        total: response.data.total,
        page: response.data.page || page,
        pageSize: response.data.page_size || pageSize,
        totalPages: response.data.total_pages || Math.ceil(response.data.total / pageSize),
        fromApi: true,
      }
    }
  } catch {
    // API cold start, offline, or timeout — gracefully proceed to local catalog
  }

  // Resilient local catalog fallback
  return filterLocalCatalog(options)
}

/**
 * Finds a single product by numeric ID or slug.
 * Checks local catalog first, then queries the backend API.
 */
export async function getProductById(id: number | string): Promise<Product | null> {
  const numId = Number(id)

  // 1. Fast local check
  if (!isNaN(numId)) {
    const local = (PRODUCTS as unknown as Product[]).find((p) => p.id === numId)
    if (local) return local
  }

  // 2. Query Backend API
  try {
    const res = await Promise.race([
      api.products.getById(numId),
      new Promise<never>((_, reject) =>
        setTimeout(() => reject(new Error('Product Detail Timeout')), 3500)
      ),
    ])
    if (res?.data?.id) {
      return adaptApiProduct(res.data)
    }
  } catch {
    // Not found in API or API offline
  }

  return null
}

/**
 * Returns all distinct categories from active catalog data.
 */
export function getCatalogCategories(): string[] {
  const set = new Set<string>()
  ;(PRODUCTS as unknown as Product[]).forEach((p) => {
    if (p.category && p.category.trim()) {
      set.add(p.category.trim())
    }
  })
  return ['all', ...Array.from(set).sort()]
}

/**
 * Returns all distinct brands from active catalog data.
 */
export function getCatalogBrands(): string[] {
  const set = new Set<string>()
  ;(PRODUCTS as unknown as Product[]).forEach((p) => {
    if (p.brand && p.brand.trim()) {
      set.add(p.brand.trim())
    }
  })
  return Array.from(set).sort()
}

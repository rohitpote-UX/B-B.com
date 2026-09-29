'use client'

import { useState, useMemo, useEffect, useCallback, useRef } from 'react'
import { useSearchParams, useRouter } from 'next/navigation'
import Link from 'next/link'
import { motion, AnimatePresence } from 'framer-motion'
import { Search, SlidersHorizontal, ArrowRight, X, ChevronLeft, ChevronRight, Sparkles } from 'lucide-react'
import { formatPrice } from '@/data/demoData'
import { handleProductImageError } from '@/lib/image-fallback'
import { trackSearch } from '@/lib/analytics'
import { searchCatalog, getCatalogCategories, CatalogQueryResult } from '@/lib/catalog'
import { Product } from '@/types'

const POPULAR_BRANDS = [
  'Samsung',
  'Apple',
  'Motorola',
  'OnePlus',
  'Xiaomi',
  'Vivo',
  'Realme',
  'Nothing',
  'Sony',
  'boAt',
  'OPPO',
  'iQOO',
]

const PAGE_SIZE = 24

export default function SearchClient() {
  const searchParams = useSearchParams()
  const router = useRouter()
  const initialQuery = searchParams.get('q') || ''
  const selectedBrand = searchParams.get('brand') || ''
  const initialPage = Math.max(1, parseInt(searchParams.get('page') || '1', 10) || 1)

  const [query, setQuery] = useState(initialQuery)
  const [sortBy, setSortBy] = useState('relevance')
  const [showFilters, setShowFilters] = useState(false)
  const [selectedCategory, setSelectedCategory] = useState('all')
  const [currentPage, setCurrentPage] = useState(initialPage)
  const [isLoading, setIsLoading] = useState(false)

  // Catalog response state
  const [catalogData, setCatalogData] = useState<CatalogQueryResult>({
    products: [],
    total: 0,
    page: 1,
    pageSize: PAGE_SIZE,
    totalPages: 1,
    fromApi: false,
  })

  useEffect(() => {
    if (selectedCategory !== 'all') {
      localStorage.setItem('bb_user_interest', selectedCategory)
    }
  }, [selectedCategory])

  // Track search queries anonymously with debounce
  useEffect(() => {
    const trimmed = query.trim()
    if (!trimmed) return
    const timer = setTimeout(() => {
      trackSearch(trimmed)
    }, 750)
    return () => clearTimeout(timer)
  }, [query])

  const categories = useMemo(() => getCatalogCategories(), [])

  // Execute catalog search (supports API query with resilient local catalog fallback)
  const executeSearch = useCallback(
    async (
      q: string,
      cat: string,
      br: string,
      sort: string,
      pg: number
    ) => {
      setIsLoading(true)
      try {
        const result = await searchCatalog({
          query: q,
          category: cat,
          brand: br,
          sortBy: sort,
          page: pg,
          pageSize: PAGE_SIZE,
        })
        setCatalogData(result)

        if (q && result.products.length > 0 && cat === 'all') {
          localStorage.setItem('bb_user_interest', result.products[0].category)
        }
      } finally {
        setIsLoading(false)
      }
    },
    []
  )

  // Trigger search on filter / query / page updates
  useEffect(() => {
    const debounceTimer = setTimeout(() => {
      executeSearch(query, selectedCategory, selectedBrand, sortBy, currentPage)
    }, 150)
    return () => clearTimeout(debounceTimer)
  }, [query, selectedCategory, selectedBrand, sortBy, currentPage, executeSearch])

  // Synchronize URL search params
  const updateSearchParams = (
    newQuery?: string,
    newBrand?: string,
    newPage: number = 1
  ) => {
    const params = new URLSearchParams()
    const qVal = newQuery !== undefined ? newQuery : query
    const bVal = newBrand !== undefined ? newBrand : selectedBrand

    if (qVal) params.set('q', qVal)
    if (bVal) params.set('brand', bVal)
    if (newPage > 1) params.set('page', newPage.toString())

    setCurrentPage(newPage)
    router.push(`/search${params.toString() ? '?' + params.toString() : ''}`, { scroll: false })
  }

  const handlePageChange = (newPage: number) => {
    if (newPage < 1 || newPage > catalogData.totalPages || newPage === currentPage) return
    setCurrentPage(newPage)
    updateSearchParams(query, selectedBrand, newPage)
    // Smooth scroll back to results anchor
    setTimeout(() => {
      document.getElementById('search-results')?.scrollIntoView({ behavior: 'smooth', block: 'start' })
    }, 50)
  }

  const { products, total, totalPages } = catalogData

  return (
    <div className="min-h-screen pt-32 pb-40">
      <div className="w-full max-w-[1536px] mx-auto px-8 md:px-16">
        {/* Header */}
        <div className="mb-24 max-w-3xl">
          <div className="flex items-center gap-3 mb-6">
            <span className="text-[0.75rem] font-medium uppercase tracking-[0.15em] text-theme-muted">
              Live Verified Catalog
            </span>
            {catalogData.fromApi && (
              <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-[#10b981]/10 text-[#10b981] border border-[#10b981]/20 text-[0.68rem] font-mono font-medium">
                <Sparkles className="w-3 h-3" /> Live Production Engine
              </span>
            )}
          </div>

          <h1 className="text-[3rem] sm:text-[4.5rem] lg:text-[5.5rem] font-[var(--font-display)] font-medium leading-[1.05] tracking-tight text-theme-text mb-12">
            {query ? `Search: ${query}` : selectedBrand ? `${selectedBrand} Products.` : 'All Products.'}
          </h1>

          <form
            onSubmit={(e) => {
              e.preventDefault()
              updateSearchParams(query, selectedBrand, 1)
            }}
            className="flex items-center border-b border-theme-border pb-8 focus-within:border-theme-text transition-colors"
          >
            <Search className="w-5 h-5 text-theme-muted mr-4 shrink-0" />
            <input
              type="text"
              value={query}
              onChange={(e) => {
                setQuery(e.target.value)
                setCurrentPage(1)
              }}
              placeholder="Search products, brands, or categories..."
              className="w-full bg-transparent text-[1.125rem] text-theme-text placeholder:text-theme-dim focus:outline-none"
            />
            <button
              type="button"
              onClick={() => setShowFilters(!showFilters)}
              className="ml-4 text-theme-secondary hover:text-theme-text transition-colors"
              aria-label="Toggle filter panel"
            >
              <SlidersHorizontal className="w-5 h-5" />
            </button>
          </form>

          {/* Always-visible Category Filter Pills */}
          <div className="mt-8 flex gap-3 overflow-x-auto hide-scrollbar pb-2">
            {categories.map((cat) => (
              <button
                key={cat}
                type="button"
                onClick={() => {
                  setSelectedCategory(cat)
                  setCurrentPage(1)
                  updateSearchParams(query, selectedBrand, 1)
                }}
                className={`shrink-0 px-5 py-2.5 text-[0.7rem] font-medium uppercase tracking-[0.12em] border transition-all duration-300 rounded-[2px] ${
                  selectedCategory === cat
                    ? 'bg-theme-text text-theme-bg border-theme-text'
                    : 'bg-transparent text-theme-secondary border-theme-border hover:border-theme-text hover:text-theme-text'
                }`}
              >
                {cat === 'all' ? 'Everything' : cat}
              </button>
            ))}
          </div>

          {/* Active Brand Filter Pill */}
          {selectedBrand && (
            <div className="mt-6 flex items-center gap-3 flex-wrap">
              <span className="text-[0.7rem] font-medium uppercase tracking-[0.12em] text-theme-muted">
                Filtered by:
              </span>
              <div className="inline-flex items-center gap-2 px-3.5 py-1.5 bg-[#ff1695]/10 border border-[#ff1695]/30 text-[#ff1695] text-[0.75rem] font-mono uppercase tracking-wider rounded-full">
                <span>Brand: {selectedBrand}</span>
                <button
                  type="button"
                  onClick={() => {
                    updateSearchParams(query, '', 1)
                  }}
                  className="hover:text-white transition-colors ml-1 p-0.5"
                  aria-label={`Remove ${selectedBrand} brand filter`}
                >
                  <X className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Filters Panel */}
        <AnimatePresence>
          {showFilters && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="overflow-hidden mb-24"
            >
              <div className="bg-theme-elevated p-12 lg:p-16 mb-12">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-16">
                  <div>
                    <label className="text-[0.75rem] font-medium uppercase tracking-[0.15em] block mb-6">
                      Category
                    </label>
                    <div className="flex flex-col gap-4">
                      {categories.map((cat) => (
                        <button
                          key={cat}
                          type="button"
                          onClick={() => {
                            setSelectedCategory(cat)
                            setCurrentPage(1)
                            updateSearchParams(query, selectedBrand, 1)
                            setShowFilters(false)
                            setTimeout(
                              () =>
                                document
                                  .getElementById('search-results')
                                  ?.scrollIntoView({ behavior: 'smooth', block: 'start' }),
                              150
                            )
                          }}
                          className={`text-left text-[0.875rem] transition-colors ${
                            selectedCategory === cat
                              ? 'text-theme-text font-medium'
                              : 'text-theme-secondary hover:text-theme-text'
                          }`}
                        >
                          {cat === 'all' ? 'Everything' : cat}
                        </button>
                      ))}
                    </div>
                  </div>
                  <div>
                    <label className="text-[0.75rem] font-medium uppercase tracking-[0.15em] block mb-6">
                      Brand
                    </label>
                    <div className="flex flex-col gap-3 max-h-56 overflow-y-auto pr-2 hide-scrollbar">
                      <button
                        type="button"
                        onClick={() => {
                          updateSearchParams(query, '', 1)
                          setShowFilters(false)
                          setTimeout(
                            () =>
                              document
                                .getElementById('search-results')
                                ?.scrollIntoView({ behavior: 'smooth', block: 'start' }),
                            150
                          )
                        }}
                        className={`text-left text-[0.875rem] transition-colors ${
                          !selectedBrand
                            ? 'text-theme-text font-medium'
                            : 'text-theme-secondary hover:text-theme-text'
                        }`}
                      >
                        All Brands
                      </button>
                      {POPULAR_BRANDS.map((b) => (
                        <button
                          key={b}
                          type="button"
                          onClick={() => {
                            updateSearchParams(query, b, 1)
                            setShowFilters(false)
                            setTimeout(
                              () =>
                                document
                                  .getElementById('search-results')
                                  ?.scrollIntoView({ behavior: 'smooth', block: 'start' }),
                              150
                            )
                          }}
                          className={`text-left text-[0.875rem] transition-colors ${
                            selectedBrand.toLowerCase() === b.toLowerCase()
                              ? 'text-theme-text font-medium'
                              : 'text-theme-secondary hover:text-theme-text'
                          }`}
                        >
                          {b}
                        </button>
                      ))}
                    </div>
                  </div>
                  <div>
                    <label className="text-[0.75rem] font-medium uppercase tracking-[0.15em] block mb-6">
                      Sort By
                    </label>
                    <div className="flex flex-col gap-4">
                      {[
                        { id: 'relevance', label: 'Relevance' },
                        { id: 'newest', label: 'Newest Releases' },
                        { id: 'deal_score', label: 'Deal Score / Hot Deals' },
                        { id: 'price_asc', label: 'Price: Low to High' },
                        { id: 'price_desc', label: 'Price: High to Low' },
                        { id: 'rating', label: 'Highest Rated' },
                      ].map((s) => (
                        <button
                          key={s.id}
                          type="button"
                          onClick={() => {
                            setSortBy(s.id)
                            setCurrentPage(1)
                            setShowFilters(false)
                            setTimeout(
                              () =>
                                document
                                  .getElementById('search-results')
                                  ?.scrollIntoView({ behavior: 'smooth', block: 'start' }),
                              150
                            )
                          }}
                          className={`text-left text-[0.875rem] transition-colors ${
                            sortBy === s.id
                              ? 'text-theme-text font-medium'
                              : 'text-theme-secondary hover:text-theme-text'
                          }`}
                        >
                          {s.label}
                        </button>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Results Metadata Bar */}
        <div
          id="search-results"
          className="text-[0.75rem] font-medium uppercase tracking-[0.15em] mb-12 pb-6 border-b border-theme-border flex justify-between items-end pt-12"
        >
          <span>
            {total} {total === 1 ? 'Product' : 'Products'} Available
            {totalPages > 1 && ` • Page ${currentPage} of ${totalPages}`}
          </span>
          {isLoading && (
            <span className="text-[#ff1695] font-mono text-[0.7rem] animate-pulse">
              Scanning Catalog...
            </span>
          )}
        </div>

        {/* Product Grid */}
        <motion.div
          layout
          className={`grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-x-12 gap-y-24 transition-opacity duration-200 ${
            isLoading ? 'opacity-60' : 'opacity-100'
          }`}
        >
          <AnimatePresence mode="popLayout">
            {products.map((product) => (
              <motion.div
                layout
                key={product.id}
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
                transition={{ duration: 0.35, ease: [0.22, 1, 0.36, 1] }}
              >
                <Link href={`/product/${product.id}`} className="group block">
                  <div className="aspect-square bg-theme-elevated p-8 lg:p-12 relative mb-8 flex items-center justify-center overflow-hidden">
                    {product.dealScore >= 85 && (
                      <div className="absolute top-6 left-6 z-10 text-[0.75rem] font-medium uppercase tracking-[0.15em] bg-theme-text text-theme-bg px-4 py-1.5">
                        Hot Deal
                      </div>
                    )}
                    <img
                      src={product.image}
                      alt={product.name}
                      className="max-w-full max-h-full object-contain group-hover:scale-110 transition-transform duration-700"
                      onError={handleProductImageError}
                      loading="lazy"
                    />
                  </div>
                  <div>
                    <h3 className="text-[1.125rem] font-medium text-theme-text tracking-tight mb-2 line-clamp-2">
                      {product.name}
                    </h3>
                    <p className="text-[0.875rem] text-theme-secondary mb-4">{product.brand}</p>
                    <div className="flex items-center justify-between">
                      <span className="text-[1.125rem] font-medium text-theme-text">
                        {formatPrice(product.bestPrice, product.currency || 'INR')}
                      </span>
                      {product.originalPrice && product.originalPrice > product.bestPrice && (
                        <span className="text-[0.875rem] text-theme-muted line-through">
                          {formatPrice(product.originalPrice, product.currency || 'INR')}
                        </span>
                      )}
                    </div>
                  </div>
                  {/* Minimal Compare CTA on Hover */}
                  <div className="mt-6 flex items-center justify-between opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                    <button
                      onClick={(e) => {
                        e.preventDefault()
                        router.push(`/compare?p1=${product.id}`)
                      }}
                      className="text-[0.75rem] font-medium uppercase tracking-wider text-theme-secondary hover:text-theme-text flex items-center gap-2"
                    >
                      Compare <ArrowRight className="w-3 h-3" />
                    </button>
                  </div>
                </Link>
              </motion.div>
            ))}
          </AnimatePresence>
        </motion.div>

        {/* Empty State */}
        {products.length === 0 && !isLoading && (
          <div className="py-32 flex flex-col items-center text-center">
            <h3 className="text-[2rem] sm:text-[3rem] lg:text-[3.5rem] font-medium leading-[1.1] tracking-tight text-theme-text mb-4">
              Nothing found.
            </h3>
            <p className="text-[1.125rem] sm:text-[1.25rem] leading-[1.6] tracking-tight max-w-md text-theme-secondary">
              Try adjusting your search query or removing filters to see more products in our verified catalog.
            </p>
            <button
              onClick={() => {
                setQuery('')
                setSelectedCategory('all')
                updateSearchParams('', '', 1)
              }}
              className="inline-flex items-center justify-center px-10 py-5 bg-transparent border border-theme-border text-theme-text text-[0.875rem] font-medium tracking-wide transition-all duration-300 rounded-[2px] hover:border-theme-text mt-8"
            >
              Clear Everything
            </button>
          </div>
        )}

        {/* Pagination Controls */}
        {totalPages > 1 && (
          <nav
            aria-label="Catalog Pagination"
            className="mt-24 pt-12 border-t border-theme-border flex flex-col sm:flex-row items-center justify-between gap-6"
          >
            <div className="text-[0.75rem] font-mono text-theme-muted">
              Showing {(currentPage - 1) * PAGE_SIZE + 1}–
              {Math.min(currentPage * PAGE_SIZE, total)} of {total} products
            </div>

            <div className="flex items-center gap-2">
              {/* Previous Page */}
              <button
                type="button"
                onClick={() => handlePageChange(currentPage - 1)}
                disabled={currentPage <= 1 || isLoading}
                aria-label="Previous Page"
                className="px-4 py-2 rounded-[2px] border border-theme-border text-xs font-mono uppercase tracking-wider text-theme-text hover:border-theme-text disabled:opacity-30 disabled:pointer-events-none transition-colors flex items-center gap-1"
              >
                <ChevronLeft className="w-4 h-4" />
                <span>Prev</span>
              </button>

              {/* Page Number Buttons */}
              <div className="flex items-center gap-1.5">
                {Array.from({ length: Math.min(5, totalPages) }, (_, idx) => {
                  let pageNum: number
                  if (totalPages <= 5) {
                    pageNum = idx + 1
                  } else if (currentPage <= 3) {
                    pageNum = idx + 1
                  } else if (currentPage >= totalPages - 2) {
                    pageNum = totalPages - 4 + idx
                  } else {
                    pageNum = currentPage - 2 + idx
                  }

                  return (
                    <button
                      key={pageNum}
                      type="button"
                      onClick={() => handlePageChange(pageNum)}
                      disabled={isLoading}
                      className={`w-9 h-9 text-xs font-mono rounded-[2px] transition-all duration-200 flex items-center justify-center ${
                        currentPage === pageNum
                          ? 'bg-[#ff1695] text-white font-bold shadow-[0_0_12px_rgba(255,22,149,0.35)]'
                          : 'border border-theme-border text-theme-secondary hover:border-theme-text hover:text-theme-text'
                      }`}
                    >
                      {pageNum}
                    </button>
                  )
                })}
              </div>

              {/* Next Page */}
              <button
                type="button"
                onClick={() => handlePageChange(currentPage + 1)}
                disabled={currentPage >= totalPages || isLoading}
                aria-label="Next Page"
                className="px-4 py-2 rounded-[2px] border border-theme-border text-xs font-mono uppercase tracking-wider text-theme-text hover:border-theme-text disabled:opacity-30 disabled:pointer-events-none transition-colors flex items-center gap-1"
              >
                <span>Next</span>
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </nav>
        )}
      </div>
    </div>
  )
}

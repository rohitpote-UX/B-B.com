'use client'

import { useState, useMemo, useEffect } from 'react'
import { useSearchParams, useRouter } from 'next/navigation'
import Link from 'next/link'
import { motion, AnimatePresence } from 'framer-motion'
import { Search, SlidersHorizontal, ArrowRight } from 'lucide-react'
import { PRODUCTS, formatPrice } from '@/data/demoData'

export default function SearchClient() {
  const searchParams = useSearchParams()
  const router = useRouter()
  const initialQuery = searchParams.get('q') || ''
  const [query, setQuery] = useState(initialQuery)
  const [sortBy, setSortBy] = useState('relevance')
  const [showFilters, setShowFilters] = useState(false)
  const [selectedCategory, setSelectedCategory] = useState('all')

  useEffect(() => {
    if (selectedCategory !== 'all') {
      localStorage.setItem('bb_user_interest', selectedCategory)
    }
  }, [selectedCategory])

  const categories = ['all', ...Array.from(new Set(PRODUCTS.map(p => p.category)))]

  const filtered = useMemo(() => {
    let results = [...PRODUCTS]
    if (query) {
      const q = query.toLowerCase()
      results = results.filter(p =>
        p.name.toLowerCase().includes(q) || p.brand.toLowerCase().includes(q) ||
        p.category.toLowerCase().includes(q)
      )
    }
    if (selectedCategory !== 'all') results = results.filter(p => p.category === selectedCategory)
    switch (sortBy) {
      case 'price_asc': results.sort((a, b) => a.bestPrice - b.bestPrice); break
      case 'price_desc': results.sort((a, b) => b.bestPrice - a.bestPrice); break
      case 'rating': results.sort((a, b) => b.rating - a.rating); break
      default: break
    }
    
    if (query && results.length > 0 && selectedCategory === 'all') {
      localStorage.setItem('bb_user_interest', results[0].category)
    }
    
    return results
  }, [query, sortBy, selectedCategory])

  const updateSearchParams = (newQuery: string) => {
    const params = new URLSearchParams()
    if (newQuery) params.set('q', newQuery)
    router.push(`/search${params.toString() ? '?' + params.toString() : ''}`, { scroll: false })
  }

  return (
    <div className="min-h-screen pt-32 pb-40">
      <div className="w-full max-w-[1536px] mx-auto px-8 md:px-16">
        {/* Header */}
        <div className="mb-24 max-w-3xl">
           <span className="text-[0.75rem] font-medium uppercase tracking-[0.15em] block mb-8">Catalog</span>
           <h1 className="text-[3rem] sm:text-[4.5rem] lg:text-[5.5rem] font-[var(--font-display)] font-medium leading-[1.05] tracking-tight text-theme-text mb-12">
             {query ? `Search: ${query}` : 'All Products.'}
           </h1>
           
           <form onSubmit={e => { e.preventDefault(); updateSearchParams(query) }} className="flex items-center border-b border-theme-border pb-8 focus-within:border-theme-text transition-colors">
              <Search className="w-5 h-5 text-theme-muted mr-4 shrink-0" />
              <input 
                type="text" 
                value={query} 
                onChange={e => setQuery(e.target.value)}
                placeholder="Search products, brands, or categories..."
                className="w-full bg-transparent text-[1.125rem] text-theme-text placeholder:text-theme-dim focus:outline-none"
              />
              <button type="button" onClick={() => setShowFilters(!showFilters)} className="ml-4 text-theme-secondary hover:text-theme-text transition-colors">
                 <SlidersHorizontal className="w-5 h-5" />
              </button>
           </form>

            {/* Always-visible Category Filter Pills */}
            <div className="mt-8 flex gap-3 overflow-x-auto hide-scrollbar pb-2">
              {categories.map(cat => (
                <button key={cat} type="button" onClick={() => {
                    setSelectedCategory(cat)
                    setQuery('')
                    updateSearchParams('')
                  }}
                  className={`shrink-0 px-5 py-2.5 text-[0.7rem] font-medium uppercase tracking-[0.12em] border transition-all duration-300 rounded-[2px] ${
                    selectedCategory === cat 
                      ? 'bg-theme-text text-theme-bg border-theme-text' 
                      : 'bg-transparent text-theme-secondary border-theme-border hover:border-theme-text hover:text-theme-text'
                  }`}
                >{cat === 'all' ? 'Everything' : cat}</button>
              ))}
            </div>
        </div>

        {/* Filters Panel */}
        <AnimatePresence>
          {showFilters && (
            <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }} exit={{ opacity: 0, height: 0 }} className="overflow-hidden mb-24">
              <div className="bg-theme-elevated p-12 lg:p-16 mb-12">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-16">
                  <div>
                    <label className="text-[0.75rem] font-medium uppercase tracking-[0.15em] block mb-6">Category</label>
                    <div className="flex flex-col gap-4">
                      {categories.map(cat => (
                        <button key={cat} type="button" onClick={() => {
                            setSelectedCategory(cat)
                            setQuery('')
                            updateSearchParams('')
                            setShowFilters(false)
                            setTimeout(() => document.getElementById('search-results')?.scrollIntoView({ behavior: 'smooth', block: 'start' }), 150)
                          }}
                          className={`text-left text-[0.875rem] transition-colors ${
                            selectedCategory === cat ? 'text-theme-text font-medium' : 'text-theme-secondary hover:text-theme-text'
                          }`}
                        >{cat === 'all' ? 'Everything' : cat}</button>
                      ))}
                    </div>
                  </div>
                  <div>
                    <label className="text-[0.75rem] font-medium uppercase tracking-[0.15em] block mb-6">Sort By</label>
                    <div className="flex flex-col gap-4">
                       {[
                         { id: 'relevance', label: 'Relevance' },
                         { id: 'price_asc', label: 'Price: Low to High' },
                         { id: 'price_desc', label: 'Price: High to Low' },
                         { id: 'rating', label: 'Highest Rated' },
                       ].map(s => (
                         <button key={s.id} type="button" onClick={() => {
                             setSortBy(s.id)
                             setShowFilters(false)
                             setTimeout(() => document.getElementById('search-results')?.scrollIntoView({ behavior: 'smooth', block: 'start' }), 150)
                           }}
                            className={`text-left text-[0.875rem] transition-colors ${
                               sortBy === s.id ? 'text-theme-text font-medium' : 'text-theme-secondary hover:text-theme-text'
                            }`}
                         >{s.label}</button>
                       ))}
                    </div>
                  </div>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        <div id="search-results" className="text-[0.75rem] font-medium uppercase tracking-[0.15em] mb-12 pb-6 border-b border-theme-border flex justify-between items-end pt-12">
           <span>{filtered.length} Results</span>
        </div>

        {/* Product Grid */}
        <motion.div layout className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-x-12 gap-y-24">
          <AnimatePresence mode="popLayout">
            {filtered.map((product) => (
              <motion.div 
                layout
                key={product.id} 
                initial={{ opacity: 0, scale: 0.9 }} 
                animate={{ opacity: 1, scale: 1 }} 
                exit={{ opacity: 0, scale: 0.9 }}
                transition={{ duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
              >
              <Link href={`/product/${product.id}`} className="group block">
                <div className="aspect-square bg-theme-elevated p-8 lg:p-12 relative mb-8 flex items-center justify-center overflow-hidden">
                  {product.dealScore >= 85 && (
                     <div className="absolute top-6 left-6 z-10 text-[0.75rem] font-medium uppercase tracking-[0.15em] bg-theme-text text-theme-bg px-4 py-1.5">Hot Deal</div>
                  )}
                  <img src={product.image} alt={product.name} className="max-w-full max-h-full object-contain group-hover:scale-110 transition-transform duration-700" />
                </div>
                <div>
                  <h3 className="text-[1.125rem] font-medium text-theme-text tracking-tight mb-2">{product.name}</h3>
                  <p className="text-[0.875rem] text-theme-secondary mb-4">{product.brand}</p>
                   <div className="flex items-center justify-between">
                     <span className="text-[1.125rem] font-medium text-theme-text">{formatPrice(product.bestPrice)}</span>
                     <span className="text-[0.875rem] text-theme-muted line-through">{formatPrice(product.originalPrice)}</span>
                   </div>
                </div>
                {/* Minimal Compare CTA on Hover */}
                <div className="mt-6 flex items-center justify-between opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                   <button onClick={(e) => { e.preventDefault(); router.push(`/compare?p1=${product.id}`) }} className="text-[0.75rem] font-medium uppercase tracking-wider text-theme-secondary hover:text-theme-text flex items-center gap-2">
                     Compare <ArrowRight className="w-3 h-3" />
                   </button>
                </div>
              </Link>
            </motion.div>
          ))}
          </AnimatePresence>
        </motion.div>

        {filtered.length === 0 && (
          <div className="py-32 flex flex-col items-center text-center">
            <h3 className="text-[2rem] sm:text-[3rem] lg:text-[3.5rem] font-medium leading-[1.1] tracking-tight text-theme-text mb-4">Nothing found.</h3>
            <p className="text-[1.125rem] sm:text-[1.25rem] leading-[1.6] tracking-tight max-w-md text-theme-secondary">Try adjusting your search query or removing filters to see more results.</p>
            <button onClick={() => { setQuery(''); setSelectedCategory('all') }} className="inline-flex items-center justify-center px-10 py-5 bg-transparent border border-theme-border text-theme-text text-[0.875rem] font-medium tracking-wide transition-all duration-300 rounded-[2px] hover:border-theme-text mt-8">Clear Everything</button>
          </div>
        )}
      </div>
    </div>
  )
}

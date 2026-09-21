'use client'

import React, { useState, useMemo } from 'react'
import Link from 'next/link'
import { motion, AnimatePresence } from 'framer-motion'
import { ShieldCheck, ArrowRight, SlidersHorizontal } from 'lucide-react'
import { formatPrice } from '@/data/demoData'

export interface BrandProductItem {
  id: number
  name: string
  category: string
  brand: string
  image: string
  bestPrice: number
  originalPrice?: number
  bestPlatform: string
  dealScore: number
  rating?: number
  totalReviews?: number
  specs?: Record<string, string | number>
}

interface BrandCatalogClientProps {
  brandName: string
  products: BrandProductItem[]
  categories: string[]
}

export default function BrandCatalogClient({
  brandName,
  products,
  categories,
}: BrandCatalogClientProps) {
  const [selectedCategory, setSelectedCategory] = useState<string>('all')
  const [sortBy, setSortBy] = useState<'featured' | 'price-asc' | 'price-desc' | 'score'>('featured')

  // Filter and sort products
  const filteredProducts = useMemo(() => {
    let list = selectedCategory === 'all'
      ? products
      : products.filter(p => (p.category || '').toLowerCase() === selectedCategory.toLowerCase())

    if (sortBy === 'price-asc') {
      list = [...list].sort((a, b) => a.bestPrice - b.bestPrice)
    } else if (sortBy === 'price-desc') {
      list = [...list].sort((a, b) => b.bestPrice - a.bestPrice)
    } else if (sortBy === 'score') {
      list = [...list].sort((a, b) => (b.dealScore || 0) - (a.dealScore || 0))
    }

    return list
  }, [products, selectedCategory, sortBy])

  return (
    <div className="space-y-8">
      {/* Category Pills & Sort Controls */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-white/10">
        {/* Category Filters */}
        <div className="flex items-center gap-2 overflow-x-auto pb-2 md:pb-0 scrollbar-none">
          <button
            onClick={() => setSelectedCategory('all')}
            className={`px-4 py-2 rounded-xl text-xs font-mono uppercase tracking-wider transition-all duration-200 whitespace-nowrap ${
              selectedCategory === 'all'
                ? 'bg-[#ff1695] text-white font-semibold shadow-[0_0_16px_rgba(255,22,149,0.35)]'
                : 'bg-white/[0.03] text-white/70 hover:text-white hover:bg-white/[0.08] border border-white/10'
            }`}
          >
            All Categories ({products.length})
          </button>
          {categories.map(cat => {
            const catCount = products.filter(p => (p.category || '').toLowerCase() === cat.toLowerCase()).length
            const isSelected = selectedCategory.toLowerCase() === cat.toLowerCase()
            return (
              <button
                key={cat}
                onClick={() => setSelectedCategory(cat)}
                className={`px-4 py-2 rounded-xl text-xs font-mono uppercase tracking-wider transition-all duration-200 whitespace-nowrap ${
                  isSelected
                    ? 'bg-[#ff1695] text-white font-semibold shadow-[0_0_16px_rgba(255,22,149,0.35)]'
                    : 'bg-white/[0.03] text-white/70 hover:text-white hover:bg-white/[0.08] border border-white/10'
                }`}
              >
                {cat} ({catCount})
              </button>
            )
          })}
        </div>

        {/* Sort Dropdown */}
        <div className="flex items-center gap-2 text-xs text-white/60 font-mono">
          <SlidersHorizontal className="w-3.5 h-3.5 text-[#ff1695]" />
          <span>Sort:</span>
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as any)}
            className="bg-[#0c0c0e] border border-white/10 rounded-lg px-3 py-1.5 text-xs text-white focus:outline-none focus:border-[#ff1695] transition cursor-pointer"
          >
            <option value="featured">Featured Catalog</option>
            <option value="price-asc">Price: Low to High</option>
            <option value="price-desc">Price: High to Low</option>
            <option value="score">Deal Confidence Score</option>
          </select>
        </div>
      </div>

      {/* Product Grid */}
      <AnimatePresence mode="wait">
        <motion.div
          key={`${selectedCategory}-${sortBy}`}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -10 }}
          transition={{ duration: 0.25 }}
          className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 sm:gap-6"
        >
          {filteredProducts.map((product) => {
            const hasDeal = product.originalPrice && product.originalPrice > product.bestPrice
            const discountPct = hasDeal
              ? Math.round(((product.originalPrice! - product.bestPrice) / product.originalPrice!) * 100)
              : null

            return (
              <Link
                key={product.id}
                href={`/product/${product.id}`}
                className="group relative flex flex-col justify-between p-5 rounded-2xl bg-white/[0.02] hover:bg-white/[0.05] border border-white/10 hover:border-[#ff1695]/40 transition-all duration-300 shadow-sm hover:shadow-[0_12px_28px_rgba(255,22,149,0.12)] hover:-translate-y-1 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#ff1695] overflow-hidden"
              >
                {/* Background Subtle Gradient Glow */}
                <div className="absolute inset-0 bg-gradient-to-br from-[#ff1695]/[0.03] to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none" />

                <div>
                  {/* Top Badges */}
                  <div className="flex items-center justify-between gap-2 mb-4">
                    <span className="text-[0.68rem] font-mono uppercase tracking-widest text-[#ff1695] font-semibold">
                      {product.category}
                    </span>
                    {product.dealScore > 0 && (
                      <span className="inline-flex items-center gap-1 text-[0.65rem] font-bold px-2 py-0.5 rounded-full bg-[#10b981]/10 text-[#10b981] border border-[#10b981]/20 font-mono">
                        <ShieldCheck className="w-3 h-3" />
                        <span>Score {product.dealScore}</span>
                      </span>
                    )}
                  </div>

                  {/* Product Image Container */}
                  <div className="w-full h-44 flex items-center justify-center p-3 rounded-xl bg-black/40 border border-white/5 mb-4 group-hover:border-white/10 transition-colors">
                    <img
                      src={product.image}
                      alt={product.name}
                      loading="lazy"
                      className="max-h-full max-w-full object-contain transition-transform duration-300 group-hover:scale-105"
                      onError={(e) => {
                        (e.target as HTMLImageElement).src =
                          'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?auto=format&fit=crop&w=600&q=80'
                      }}
                    />
                  </div>

                  {/* Product Title */}
                  <h3 className="text-sm sm:text-base font-semibold text-white group-hover:text-[#ff1695] transition-colors line-clamp-2 mb-2 leading-snug">
                    {product.name}
                  </h3>

                  {/* Key Spec Snippet if present */}
                  {product.specs && (
                    <p className="text-xs text-white/50 line-clamp-1 mb-3 font-mono">
                      {(product.specs as any)['Processor'] || (product.specs as any)['Display'] || (product.specs as any)['Battery'] || (product.specs as any)['Colour'] || ''}
                    </p>
                  )}
                </div>

                {/* Pricing & Footer */}
                <div className="pt-4 border-t border-white/[0.08] mt-2">
                  <div className="flex items-baseline justify-between gap-2">
                    <div>
                      <span className="text-xs text-white/40 font-mono block">Lowest Verified</span>
                      <div className="text-lg font-bold text-white font-[var(--font-display)]">
                        {formatPrice(product.bestPrice)}
                      </div>
                    </div>
                    {hasDeal && discountPct && (
                      <div className="text-right">
                        <span className="text-xs text-white/40 line-through block font-mono">
                          {formatPrice(product.originalPrice!)}
                        </span>
                        <span className="text-xs text-[#10b981] font-semibold font-mono">
                          {discountPct}% OFF
                        </span>
                      </div>
                    )}
                  </div>

                  {/* Action row */}
                  <div className="flex items-center justify-between mt-3 text-xs font-mono text-white/50 group-hover:text-white transition-colors">
                    <span className="capitalize">{product.bestPlatform || 'Verified Store'}</span>
                    <span className="flex items-center gap-1 text-[#ff1695] group-hover:translate-x-1 transition-transform">
                      <span>View Intel</span>
                      <ArrowRight className="w-3.5 h-3.5" />
                    </span>
                  </div>
                </div>
              </Link>
            )
          })}
        </motion.div>
      </AnimatePresence>

      {filteredProducts.length === 0 && (
        <div className="p-12 text-center rounded-2xl bg-white/[0.02] border border-white/10 text-white/60">
          <p className="text-sm">No products found for this category filter.</p>
        </div>
      )}
    </div>
  )
}

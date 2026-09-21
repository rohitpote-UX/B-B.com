'use client'

import React, { useMemo } from 'react'
import Link from 'next/link'
import { motion } from 'framer-motion'
import { ArrowRight } from 'lucide-react'
import { PRODUCTS } from '@/data/demoData'

interface BrandItem {
  id: string
  name: string
  slug: string
}

// Curated hardware manufacturers
const BRAND_DEFINITIONS: BrandItem[] = [
  { id: 'samsung', name: 'Samsung', slug: 'Samsung' },
  { id: 'apple', name: 'Apple', slug: 'Apple' },
  { id: 'motorola', name: 'Motorola', slug: 'Motorola' },
  { id: 'oneplus', name: 'OnePlus', slug: 'OnePlus' },
  { id: 'xiaomi', name: 'Xiaomi', slug: 'Xiaomi' },
  { id: 'vivo', name: 'Vivo', slug: 'Vivo' },
  { id: 'realme', name: 'Realme', slug: 'Realme' },
  { id: 'nothing', name: 'Nothing', slug: 'Nothing' },
  { id: 'sony', name: 'Sony', slug: 'Sony' },
  { id: 'boat', name: 'boAt', slug: 'boAt' },
  { id: 'oppo', name: 'OPPO', slug: 'OPPO' },
  { id: 'iqoo', name: 'iQOO', slug: 'iQOO' },
]

export default function BrowseByBrand() {
  // Compute genuine product counts per brand directly from active catalog data
  const brandStats = useMemo(() => {
    const counts: Record<string, number> = {}
    BRAND_DEFINITIONS.forEach((brand) => {
      const slugLower = brand.slug.toLowerCase()
      const total = PRODUCTS.filter((p) => {
        const prodBrandLower = (p.brand || '').toLowerCase()
        if (slugLower === 'nothing') {
          return prodBrandLower === 'nothing' || prodBrandLower === 'cmf by nothing'
        }
        return prodBrandLower === slugLower
      }).length
      counts[brand.id] = total
    })
    return counts
  }, [])

  return (
    <section
      id="browse-by-brand"
      aria-labelledby="browse-by-brand-heading"
      className="relative py-20 sm:py-24 bg-[#050505] text-white border-b border-white/10 overflow-hidden"
    >
      {/* Background ambient lighting */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-[#ff1695]/[0.03] via-transparent to-transparent pointer-events-none" />

      <div className="w-full max-w-[1536px] mx-auto px-6 sm:px-10 lg:px-16 relative z-10">
        {/* Section Header */}
        <div className="flex flex-col sm:flex-row sm:items-end justify-between mb-10 sm:mb-12 gap-6">
          <div>
            <div className="flex items-center gap-2 mb-3">
              <span className="text-[#ff1695] font-mono text-xs tracking-widest font-semibold uppercase">
                EXPLORE BRANDS
              </span>
              <span className="text-white/30 text-xs">/</span>
              <span className="text-white/60 font-mono text-xs tracking-widest uppercase">
                HARDWARE ECOSYSTEMS
              </span>
            </div>
            <h2
              id="browse-by-brand-heading"
              className="text-3xl sm:text-4xl md:text-5xl font-[var(--font-display)] font-semibold tracking-tight uppercase"
            >
              Browse by <span className="text-[#ff1695] italic">Brand.</span>
            </h2>
            <p className="text-sm sm:text-base text-white/60 max-w-2xl font-light mt-4 leading-relaxed">
              Start with the brands you already trust. Explore their products, compare what matters, and decide with confidence.
            </p>
          </div>

          <Link
            href="/search"
            className="inline-flex items-center gap-2 text-xs font-mono uppercase tracking-wider text-white/70 hover:text-white transition-colors group"
          >
            <span>Explore All Products</span>
            <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-1" />
          </Link>
        </div>

        {/* Responsive Brand Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3 sm:gap-4 lg:gap-5">
          {BRAND_DEFINITIONS.map((brand, idx) => {
            const count = brandStats[brand.id] || 0

            return (
              <motion.div
                key={brand.id}
                initial={{ opacity: 0, y: 15 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: '-50px' }}
                transition={{ duration: 0.4, delay: (idx % 6) * 0.05 }}
              >
                <Link
                  href={`/brand/${brand.slug.toLowerCase()}`}
                  aria-label={`Browse ${brand.name} products (${count} available)`}
                  className="group relative flex flex-col justify-between p-4 sm:p-5 rounded-xl bg-white/[0.02] hover:bg-white/[0.05] border border-white/10 hover:border-[#ff1695]/40 transition-all duration-300 shadow-sm hover:shadow-[0_12px_24px_rgba(255,22,149,0.12)] hover:-translate-y-1 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#ff1695] min-h-[108px] sm:min-h-[116px] overflow-hidden"
                >
                  {/* Subtle hover gradient glow inside card */}
                  <div className="absolute inset-0 bg-gradient-to-br from-[#ff1695]/[0.04] to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none" />

                  {/* Brand Name */}
                  <div>
                    <h3 className="text-base sm:text-lg font-semibold text-white tracking-tight group-hover:text-white transition-colors">
                      {brand.name}
                    </h3>
                  </div>

                  {/* Product Count & Action Affordance */}
                  <div className="flex items-center justify-between mt-4 pt-3 border-t border-white/[0.06] text-xs font-mono">
                    <span className="text-white/50 group-hover:text-white/80 transition-colors">
                      {count} {count === 1 ? 'product' : 'products'}
                    </span>
                    <span className="text-white/30 group-hover:text-[#ff1695] flex items-center group-hover:translate-x-1 transition-all duration-300">
                      <ArrowRight className="w-3.5 h-3.5" />
                    </span>
                  </div>
                </Link>
              </motion.div>
            )
          })}
        </div>
      </div>
    </section>
  )
}

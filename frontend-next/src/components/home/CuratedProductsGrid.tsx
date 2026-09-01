'use client'

import { motion } from 'framer-motion'
import Link from 'next/link'
import { ArrowRight, Tag, Star, ArrowLeftRight } from 'lucide-react'
import { PRODUCTS, DEALS, formatPrice } from '@/data/demoData'

export default function CuratedProductsGrid() {
  const showcaseProducts = PRODUCTS.slice(0, 8)

  return (
    <section className="relative py-28 bg-[#050505] text-white border-b border-white/10">
      <div className="w-full max-w-[1536px] mx-auto px-6 sm:px-10 lg:px-16">
        
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-end justify-between mb-16 gap-6">
          <div>
            <div className="flex items-center gap-2 mb-3">
              <span className="text-[#ff1695] font-mono text-xs tracking-widest font-semibold uppercase">
                CURATED CATALOG
              </span>
              <span className="text-white/30 text-xs">/</span>
              <span className="text-white/60 font-mono text-xs tracking-widest uppercase">
                VERIFIED HARDWARE
              </span>
            </div>
            <h2 className="text-3xl sm:text-4xl md:text-5xl font-[var(--font-display)] font-semibold tracking-tight uppercase">
              Curated Intelligence <span className="text-[#ff1695] italic">Selection.</span>
            </h2>
          </div>

          <Link
            href="/search"
            className="inline-flex items-center gap-2 text-xs font-mono uppercase tracking-wider text-white/70 hover:text-white transition-colors group"
          >
            <span>Explore All 1,460+ Products</span>
            <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-1" />
          </Link>
        </div>

        {/* 12-Column Responsive Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 lg:gap-8">
          {showcaseProducts.map((product, idx) => (
            <motion.div
              key={product.id}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: (idx % 4) * 0.08 }}
            >
              <Link
                href={`/product/${product.id}`}
                className="group relative block rounded-3xl bg-white/[0.02] hover:bg-white/[0.04] border border-white/10 hover:border-[#ff1695]/40 p-6 backdrop-blur-xl transition-all duration-500 shadow-lg hover:shadow-[0_20px_40px_rgba(255,22,149,0.15)] hover:-translate-y-1 overflow-hidden h-full flex flex-col justify-between"
              >
                {/* Floating Deal Score / Discount Badge */}
                <div className="flex items-center justify-between mb-4">
                  <span className="text-[0.65rem] font-mono uppercase tracking-wider bg-white/10 text-white/80 px-2.5 py-1 rounded-full border border-white/10">
                    {product.brand}
                  </span>
                  {product.dealScore && (
                    <span className="text-[0.65rem] font-mono font-bold uppercase bg-[#ff1695]/20 text-[#ff1695] px-2.5 py-1 rounded-full border border-[#ff1695]/30 flex items-center gap-1">
                      <Tag className="w-3 h-3" />
                      <span>{product.dealScore}% Score</span>
                    </span>
                  )}
                </div>

                {/* Image Container with Soft Glass Framing & Zoom */}
                <div className="relative aspect-square w-full rounded-2xl bg-white/[0.02] p-6 mb-6 flex items-center justify-center overflow-hidden border border-white/[0.05]">
                  <img
                    src={product.image}
                    alt={product.name}
                    className="max-h-full max-w-full object-contain filter drop-shadow-xl group-hover:scale-110 transition-transform duration-700 ease-out"
                  />
                </div>

                {/* Content */}
                <div>
                  <div className="flex items-center gap-1 text-amber-400 text-xs font-mono mb-2">
                    <Star className="w-3.5 h-3.5 fill-amber-400" />
                    <span>{product.rating}</span>
                    <span className="text-white/40 font-light">({product.totalReviews?.toLocaleString()})</span>
                  </div>

                  <h3 className="text-base font-bold text-white group-hover:text-[#ff1695] transition-colors line-clamp-2 leading-snug">
                    {product.name}
                  </h3>

                  <div className="mt-4 pt-4 border-t border-white/10 flex items-center justify-between">
                    <div>
                      <span className="text-[0.65rem] font-mono text-white/40 uppercase block">Best Market Price</span>
                      <span className="text-lg font-mono font-bold text-white">{formatPrice(product.bestPrice)}</span>
                    </div>

                    <div className="p-2 rounded-xl bg-white/10 group-hover:bg-[#ff1695] group-hover:text-white transition-colors text-white/80">
                      <ArrowLeftRight className="w-4 h-4" />
                    </div>
                  </div>
                </div>

                {/* Subtle border sheen on hover */}
                <div className="absolute inset-0 rounded-3xl bg-gradient-to-r from-[#ff1695]/0 via-[#ff1695]/10 to-[#ff1695]/0 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none" />
              </Link>
            </motion.div>
          ))}
        </div>

      </div>
    </section>
  )
}

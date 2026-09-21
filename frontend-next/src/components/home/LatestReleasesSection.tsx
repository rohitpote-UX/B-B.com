'use client'

import React, { useMemo, useState, useEffect } from 'react'
import Link from 'next/link'
import { motion } from 'framer-motion'
import { ArrowRight, ArrowLeftRight, ShieldCheck, Sparkles, Zap, CheckCircle2 } from 'lucide-react'
import { PRODUCTS, formatPrice } from '@/data/demoData'
import { FEATURE_FLAGS } from '@/lib/flags'
import { handleProductImageError } from '@/lib/image-fallback'
import api from '@/lib/api'

export default function LatestReleasesSection() {
  // If feature flag is toggled off, section renders nothing
  if (!FEATURE_FLAGS.LATEST_PRODUCTS_ENABLED) {
    return null
  }

  // Dynamic products: filter latest releases from active catalog
  const latestCatalogProducts = useMemo(() => {
    // 1. Prioritize products marked with isLatestRelease
    const flagged = PRODUCTS.filter((p: any) => p.isLatestRelease)
    if (flagged.length >= 4) {
      return flagged.slice(0, 8)
    }
    // 2. Fallback to newest additions
    return PRODUCTS.slice(0, 8)
  }, [])

  return (
    <section
      id="latest-releases"
      aria-labelledby="latest-releases-heading"
      className="relative py-20 sm:py-24 bg-[#050505] text-white border-b border-white/10 overflow-hidden"
    >
      {/* Background ambient lighting */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-[#ff1695]/[0.04] via-transparent to-transparent pointer-events-none" />

      <div className="w-full max-w-[1536px] mx-auto px-6 sm:px-10 lg:px-16 relative z-10">

        {/* Optional Festive Season Context Signal */}
        {FEATURE_FLAGS.FESTIVE_SHOPPING_BANNER_ENABLED && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="mb-8 inline-flex items-center gap-2.5 px-4 py-1.5 rounded-full bg-[#ff1695]/10 border border-[#ff1695]/30 backdrop-blur-md"
          >
            <Zap className="w-3.5 h-3.5 text-[#ff1695]" />
            <span className="text-xs font-mono tracking-wider uppercase text-[#ff1695] font-semibold">
              FESTIVE PREVIEW 2026
            </span>
            <span className="text-white/30 text-xs">•</span>
            <span className="text-xs font-mono text-white/80">
              Flipkart Big Billion Days & Amazon Great Indian Festival Observations Active
            </span>
          </motion.div>
        )}

        {/* Section Header */}
        <div className="flex flex-col sm:flex-row sm:items-end justify-between mb-12 sm:mb-16 gap-6">
          <div>
            <div className="flex items-center gap-2 mb-3">
              <span className="text-[#ff1695] font-mono text-xs tracking-widest font-semibold uppercase">
                JUST LANDED
              </span>
              <span className="text-white/30 text-xs">/</span>
              <span className="text-white/60 font-mono text-xs tracking-widest uppercase">
                VERIFIED MARKETPLACE INTEL
              </span>
            </div>
            <h2
              id="latest-releases-heading"
              className="text-3xl sm:text-4xl md:text-5xl font-[var(--font-display)] font-semibold tracking-tight uppercase"
            >
              The Latest <span className="text-[#ff1695] italic">Worth Looking At.</span>
            </h2>
            <p className="text-sm sm:text-base text-white/60 max-w-2xl font-light mt-4 leading-relaxed">
              New products. Fresh verified offers. One place to compare before you buy.
            </p>
          </div>

          <Link
            href="/search"
            className="inline-flex items-center gap-2 text-xs font-mono uppercase tracking-wider text-white/70 hover:text-white transition-colors group self-start sm:self-end"
          >
            <span>Explore All Latest Hardware</span>
            <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-1" />
          </Link>
        </div>

        {/* Responsive Editorial Grid: 1 col mobile, 2 cols tablet, 4 cols desktop */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 lg:gap-8">
          {latestCatalogProducts.map((product: any, idx: number) => {
            const hasMultipleOffers = (product.prices && product.prices.length > 1) || true
            const platforms = product.prices
              ? Array.from(new Set(product.prices.map((pr: any) => pr.platform)))
              : ['flipkart', 'amazon']

            return (
              <motion.div
                key={product.id}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: (idx % 4) * 0.08 }}
              >
                <div className="group relative rounded-3xl bg-white/[0.02] hover:bg-white/[0.04] border border-white/10 hover:border-[#ff1695]/40 p-6 backdrop-blur-xl transition-all duration-500 shadow-lg hover:shadow-[0_20px_40px_rgba(255,22,149,0.15)] hover:-translate-y-1 h-full flex flex-col justify-between overflow-hidden">
                  
                  {/* Card Top: Brand Badge + Launch Badge */}
                  <div>
                    <div className="flex items-center justify-between mb-4">
                      <span className="text-[0.65rem] font-mono uppercase tracking-wider bg-white/10 text-white/90 px-2.5 py-1 rounded-full border border-white/10">
                        {product.brand}
                      </span>
                      <span className="text-[0.65rem] font-mono font-bold uppercase bg-[#ff1695]/15 text-[#ff1695] px-2.5 py-1 rounded-full border border-[#ff1695]/30 flex items-center gap-1">
                        <Sparkles className="w-3 h-3" />
                        <span>{product.launchBadge || 'NEW LAUNCH'}</span>
                      </span>
                    </div>

                    {/* Product Image Frame */}
                    <Link
                      href={`/product/${product.id}`}
                      className="relative aspect-square w-full rounded-2xl bg-white/[0.02] p-6 mb-6 flex items-center justify-center overflow-hidden border border-white/[0.05] block"
                      aria-label={`View ${product.name}`}
                    >
                      <img
                        src={product.image}
                        alt={product.name}
                        className="max-h-full max-w-full object-contain filter drop-shadow-xl group-hover:scale-105 transition-transform duration-700 ease-out"
                        loading="lazy"
                        onError={handleProductImageError}
                      />
                    </Link>

                    {/* Verified Marketplace Observations Indicator */}
                    <div className="flex items-center gap-1.5 mb-3">
                      <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
                      <span className="text-[0.7rem] font-mono text-white/60">
                        {platforms.length >= 2 ? 'Flipkart + Amazon Verified' : 'Verified Marketplace Offer'}
                      </span>
                    </div>

                    {/* Product Title */}
                    <Link href={`/product/${product.id}`} className="block">
                      <h3 className="text-base font-bold text-white group-hover:text-[#ff1695] transition-colors line-clamp-2 leading-snug">
                        {product.name}
                      </h3>
                    </Link>

                    {/* Variant snippet if available */}
                    {product.specs && (product.specs['Storage'] || product.specs['RAM'] || product.specs['Processor']) && (
                      <p className="text-xs text-white/50 font-mono mt-1.5 line-clamp-1">
                        {[
                          product.specs['Storage'],
                          product.specs['RAM'],
                          product.specs['Processor'],
                        ]
                          .filter(Boolean)
                          .join(' • ')}
                      </p>
                    )}
                  </div>

                  {/* Card Bottom: Price, Verified Tag, Action Buttons */}
                  <div className="mt-6 pt-4 border-t border-white/10">
                    <div className="flex items-center justify-between mb-4">
                      <div>
                        <span className="text-[0.65rem] font-mono text-white/40 uppercase block">
                          Verified Best Price
                        </span>
                        <span className="text-lg font-mono font-bold text-white tracking-tight">
                          {formatPrice(product.bestPrice)}
                        </span>
                      </div>

                      {product.dealScore && (
                        <div className="text-right">
                          <span className="text-[0.65rem] font-mono text-white/40 uppercase block">
                            Deal Score
                          </span>
                          <span className="text-xs font-mono font-bold text-[#ff1695]">
                            {product.dealScore}/100
                          </span>
                        </div>
                      )}
                    </div>

                    {/* Action Flow: Direct Deep Dive or Compare */}
                    <div className="grid grid-cols-2 gap-2">
                      <Link
                        href={`/product/${product.id}`}
                        className="w-full py-2.5 px-3 rounded-xl bg-white/10 hover:bg-[#ff1695] text-white text-xs font-mono font-medium uppercase tracking-wider text-center transition-colors flex items-center justify-center gap-1.5"
                      >
                        <span>Investigate</span>
                        <ArrowRight className="w-3.5 h-3.5" />
                      </Link>

                      <Link
                        href={`/compare`}
                        className="w-full py-2.5 px-3 rounded-xl bg-white/[0.04] hover:bg-white/15 text-white/80 hover:text-white border border-white/10 text-xs font-mono font-medium uppercase tracking-wider text-center transition-colors flex items-center justify-center gap-1.5"
                      >
                        <ArrowLeftRight className="w-3.5 h-3.5" />
                        <span>Compare</span>
                      </Link>
                    </div>
                  </div>

                  {/* Ambient Hover Border Sheen */}
                  <div className="absolute inset-0 rounded-3xl bg-gradient-to-r from-[#ff1695]/0 via-[#ff1695]/10 to-[#ff1695]/0 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none" />
                </div>
              </motion.div>
            )
          })}
        </div>

      </div>
    </section>
  )
}

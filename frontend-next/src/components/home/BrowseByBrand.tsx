'use client'

import React, { useMemo } from 'react'
import Link from 'next/link'
import { motion } from 'framer-motion'
import { ArrowRight, Sparkles } from 'lucide-react'
import { PRODUCTS } from '@/data/demoData'

interface BrandItem {
  id: string
  name: string
  slug: string
  tagline: string
  logo: React.ReactNode
}

// Authentic SVG vector marks for curated brands
const BRAND_DEFINITIONS: BrandItem[] = [
  {
    id: 'samsung',
    name: 'Samsung',
    slug: 'Samsung',
    tagline: 'Galaxy Ecosystem & Displays',
    logo: (
      <svg className="w-auto h-5 fill-current" viewBox="0 0 160 36" xmlns="http://www.w3.org/2000/svg">
        <text
          x="0"
          y="28"
          fontFamily="system-ui, -apple-system, sans-serif"
          fontWeight="900"
          fontSize="30"
          letterSpacing="0.14em"
        >
          SAMSUNG
        </text>
      </svg>
    ),
  },
  {
    id: 'apple',
    name: 'Apple',
    slug: 'Apple',
    tagline: 'Silicon & Premium Hardware',
    logo: (
      <svg className="w-6 h-6 fill-current" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
        <path d="M18.71 19.5c-.83 1.24-1.71 2.45-3.05 2.47-1.34.03-1.77-.79-3.29-.79-1.53 0-2 .77-3.27.82-1.31.05-2.3-1.32-3.14-2.53C4.25 17 2.94 12.45 4.7 9.39c.87-1.52 2.43-2.48 4.12-2.51 1.28-.02 2.5.87 3.29.87.78 0 2.26-1.07 3.81-.91.65.03 2.47.26 3.64 1.98-.09.06-2.17 1.28-2.15 3.81.03 3.02 2.65 4.03 2.68 4.04-.03.07-.42 1.44-1.38 2.83M15.97 6.37c.63-.76 1.06-1.82.94-2.87-.91.04-2.02.6-2.67 1.36-.58.67-.99 1.74-.85 2.79 1.02.08 2.05-.52 2.58-1.28" />
      </svg>
    ),
  },
  {
    id: 'motorola',
    name: 'Motorola',
    slug: 'Motorola',
    tagline: 'Edge & G-Series Innovation',
    logo: (
      <svg className="w-7 h-7 fill-current" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
        <circle cx="12" cy="12" r="11" fill="none" stroke="currentColor" strokeWidth="1.6" />
        <path d="M12 6.5c-1.3 0-2.5 1.5-3.3 3.6L6.5 15h2.1l1.5-3.8c.6-1.5 1.3-2.3 1.9-2.3.6 0 1.3.8 1.9 2.3l1.5 3.8h2.1l-2.2-4.9c-.8-2.1-2-3.6-3.3-3.6z" />
        <path d="M12 9.5c-.8 0-1.5.8-2 2l-1 2.5h1.6l.6-1.5c.3-.8.6-1.2.8-1.2.3 0 .6.4.8 1.2l.6 1.5H15l-1-2.5c-.5-1.2-1.2-2-2-2z" />
      </svg>
    ),
  },
  {
    id: 'oneplus',
    name: 'OnePlus',
    slug: 'OnePlus',
    tagline: 'Flagship Speed & Fluidity',
    logo: (
      <svg className="w-auto h-5 fill-current" viewBox="0 0 130 32" xmlns="http://www.w3.org/2000/svg">
        <text
          x="0"
          y="25"
          fontFamily="system-ui, -apple-system, sans-serif"
          fontWeight="800"
          fontSize="26"
          letterSpacing="0.05em"
        >
          ONEPLUS
        </text>
      </svg>
    ),
  },
  {
    id: 'xiaomi',
    name: 'Xiaomi',
    slug: 'Xiaomi',
    tagline: 'Smart Living & Flagships',
    logo: (
      <svg className="w-7 h-7" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
        <rect x="2" y="2" width="20" height="20" rx="6" fill="#ff6900" />
        <path
          d="M7 8h3v5.5c0 .8.7 1.5 1.5 1.5s1.5-.7 1.5-1.5V8h3v5.5c0 2.5-2 4.5-4.5 4.5S7 16 7 13.5V8zm7 5.5h-1.5v-3H14v3z"
          fill="#ffffff"
        />
      </svg>
    ),
  },
  {
    id: 'vivo',
    name: 'Vivo',
    slug: 'Vivo',
    tagline: 'ZEISS Mobile Photography',
    logo: (
      <svg className="w-auto h-5 fill-current" viewBox="0 0 100 32" xmlns="http://www.w3.org/2000/svg">
        <text
          x="0"
          y="25"
          fontFamily="system-ui, -apple-system, sans-serif"
          fontWeight="800"
          fontSize="28"
          letterSpacing="0.08em"
        >
          vivo
        </text>
      </svg>
    ),
  },
  {
    id: 'realme',
    name: 'Realme',
    slug: 'Realme',
    tagline: 'High-Refresh Gaming Tech',
    logo: (
      <svg className="w-auto h-5 fill-current" viewBox="0 0 110 32" xmlns="http://www.w3.org/2000/svg">
        <text
          x="0"
          y="25"
          fontFamily="system-ui, -apple-system, sans-serif"
          fontWeight="800"
          fontSize="26"
          letterSpacing="0.05em"
        >
          realme
        </text>
      </svg>
    ),
  },
  {
    id: 'nothing',
    name: 'Nothing',
    slug: 'Nothing',
    tagline: 'Glyph Interface & Design',
    logo: (
      <svg className="w-auto h-5 fill-current" viewBox="0 0 130 32" xmlns="http://www.w3.org/2000/svg">
        <text
          x="0"
          y="25"
          fontFamily="monospace, system-ui, sans-serif"
          fontWeight="700"
          fontSize="24"
          letterSpacing="0.22em"
        >
          NOTHING
        </text>
      </svg>
    ),
  },
  {
    id: 'sony',
    name: 'Sony',
    slug: 'Sony',
    tagline: 'Pro Audio & BRAVIA Tech',
    logo: (
      <svg className="w-auto h-5 fill-current" viewBox="0 0 110 32" xmlns="http://www.w3.org/2000/svg">
        <text
          x="0"
          y="25"
          fontFamily="Georgia, serif"
          fontWeight="900"
          fontSize="28"
          letterSpacing="0.12em"
        >
          SONY
        </text>
      </svg>
    ),
  },
  {
    id: 'boat',
    name: 'boAt',
    slug: 'boAt',
    tagline: 'Signature Bass & Wearables',
    logo: (
      <svg className="w-auto h-5 fill-current" viewBox="0 0 95 32" xmlns="http://www.w3.org/2000/svg">
        <text
          x="0"
          y="25"
          fontFamily="system-ui, -apple-system, sans-serif"
          fontWeight="800"
          fontSize="28"
          letterSpacing="0.02em"
        >
          bo<span className="text-[#ff1695]">A</span>t
        </text>
      </svg>
    ),
  },
  {
    id: 'oppo',
    name: 'OPPO',
    slug: 'OPPO',
    tagline: 'Camera Tech & SuperVOOC',
    logo: (
      <svg className="w-auto h-5 fill-current" viewBox="0 0 105 32" xmlns="http://www.w3.org/2000/svg">
        <text
          x="0"
          y="25"
          fontFamily="system-ui, -apple-system, sans-serif"
          fontWeight="700"
          fontSize="28"
          letterSpacing="0.12em"
        >
          OPPO
        </text>
      </svg>
    ),
  },
  {
    id: 'iqoo',
    name: 'iQOO',
    slug: 'iQOO',
    tagline: 'Ultra Esports Performance',
    logo: (
      <svg className="w-auto h-5 fill-current" viewBox="0 0 95 32" xmlns="http://www.w3.org/2000/svg">
        <text
          x="0"
          y="25"
          fontFamily="system-ui, -apple-system, sans-serif"
          fontWeight="900"
          fontStyle="italic"
          fontSize="27"
          letterSpacing="0.08em"
        >
          iQOO
        </text>
      </svg>
    ),
  },
]

export default function BrowseByBrand() {
  // Compute genuine product counts per brand directly from catalog data
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
      className="relative py-24 sm:py-28 bg-[#050505] text-white border-b border-white/10 overflow-hidden"
    >
      {/* Background ambient lighting */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-[#ff1695]/[0.03] via-transparent to-transparent pointer-events-none" />

      <div className="w-full max-w-[1536px] mx-auto px-6 sm:px-10 lg:px-16 relative z-10">
        {/* Section Header */}
        <div className="flex flex-col sm:flex-row sm:items-end justify-between mb-12 sm:mb-16 gap-6">
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
                  href={`/search?brand=${encodeURIComponent(brand.slug)}`}
                  aria-label={`Browse ${brand.name} products (${count} available)`}
                  className="group relative flex flex-col justify-between p-4 sm:p-5 rounded-2xl bg-white/[0.02] hover:bg-white/[0.05] border border-white/10 hover:border-[#ff1695]/40 transition-all duration-300 shadow-sm hover:shadow-[0_12px_24px_rgba(255,22,149,0.12)] hover:-translate-y-1 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#ff1695] h-full min-h-[140px] sm:min-h-[156px] overflow-hidden"
                >
                  {/* Subtle hover gradient glow inside card */}
                  <div className="absolute inset-0 bg-gradient-to-br from-[#ff1695]/[0.04] to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none" />

                  {/* Brand Mark Area */}
                  <div className="flex items-center justify-between gap-2 mb-3">
                    <div className="h-7 sm:h-8 flex items-center text-white/80 group-hover:text-white group-hover:scale-105 transition-all duration-300 origin-left">
                      {brand.logo}
                    </div>
                    <Sparkles className="w-3.5 h-3.5 text-[#ff1695]/0 group-hover:text-[#ff1695]/80 transition-all duration-300 shrink-0" />
                  </div>

                  {/* Brand Meta & Count */}
                  <div>
                    <h3 className="text-sm sm:text-base font-medium text-white tracking-tight group-hover:text-white transition-colors">
                      {brand.name}
                    </h3>
                    <p className="text-[0.65rem] sm:text-[0.7rem] text-white/45 font-light mt-0.5 line-clamp-1">
                      {brand.tagline}
                    </p>

                    {/* Bottom Action Affordance */}
                    <div className="flex items-center justify-between mt-3 pt-2.5 border-t border-white/[0.06] text-[0.65rem] sm:text-xs font-mono">
                      <span className="text-white/50 group-hover:text-white/80 transition-colors">
                        {count} {count === 1 ? 'product' : 'products'}
                      </span>
                      <span className="text-white/30 group-hover:text-[#ff1695] flex items-center gap-1 group-hover:translate-x-0.5 transition-all duration-300">
                        <ArrowRight className="w-3 h-3" />
                      </span>
                    </div>
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

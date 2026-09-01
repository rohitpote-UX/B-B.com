'use client'

import { motion } from 'framer-motion'
import Link from 'next/link'
import { ArrowRight, Sparkles, ShieldCheck, TrendingDown, Cpu, CheckCircle2 } from 'lucide-react'
import { PRODUCTS, formatPrice } from '@/data/demoData'

export default function HeroSection() {
  const heroProduct = PRODUCTS[0] || {
    name: 'Sony WH-1000XM5 Wireless Headphones',
    brand: 'SONY',
    bestPrice: 299.99,
    originalPrice: 399.99,
    image: 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?q=80&w=800&auto=format&fit=crop',
    rating: 4.8,
  }

  const competitorProduct = PRODUCTS[1] || {
    name: 'Apple AirPods Max',
    brand: 'APPLE',
    bestPrice: 479.00,
    originalPrice: 549.00,
    image: 'https://images.unsplash.com/photo-1546435770-a3e426bf472b?q=80&w=800&auto=format&fit=crop',
    rating: 4.6,
  }

  return (
    <section className="relative min-h-[92vh] flex items-center justify-center pt-24 sm:pt-28 pb-12 sm:pb-16 overflow-hidden bg-[#050505] text-white">
      {/* ── Background Glow & Radial Light ── */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[320px] sm:w-[600px] lg:w-[800px] h-[300px] sm:h-[400px] lg:h-[500px] bg-[#ff1695]/10 blur-[100px] sm:blur-[140px] rounded-full pointer-events-none" />
      <div className="absolute top-1/3 right-10 w-[250px] sm:w-[400px] h-[250px] sm:h-[400px] bg-rose-900/10 blur-[100px] sm:blur-[120px] rounded-full pointer-events-none" />

      {/* ── Fine Grid Lines & Noise Overlay ── */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#ffffff05_1px,transparent_1px),linear-gradient(to_bottom,#ffffff05_1px,transparent_1px)] bg-[size:3rem_3rem] sm:bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_100%)] pointer-events-none" />

      <div className="w-full max-w-[1536px] mx-auto px-4 sm:px-8 md:px-12 lg:px-16 relative z-10">
        <div className="grid grid-cols-12 gap-6 lg:gap-12 items-center">
          
          {/* ── LEFT: EDITORIAL TYPOGRAPHY & CTAs ── */}
          <div className="col-span-12 lg:col-span-7 flex flex-col justify-center">
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
            >
              {/* Small Label with Glowing Live Indicator */}
              <div className="inline-flex items-center gap-2.5 px-3 py-1.5 rounded-full bg-white/[0.04] border border-white/10 backdrop-blur-md mb-6 sm:mb-8">
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#ff1695] opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-[#ff1695]"></span>
                </span>
                <span className="text-[0.65rem] sm:text-[0.75rem] font-mono tracking-widest uppercase text-white/80">
                  AI Product Intelligence Engine v4.0
                </span>
              </div>

              {/* Massive Editorial Headline - Fluid Scaling */}
              <h1 className="text-[2.2rem] sm:text-[4rem] md:text-[5.2rem] lg:text-[6rem] xl:text-[6.2rem] font-[var(--font-display)] font-semibold tracking-tight uppercase leading-[0.98] sm:leading-[0.95] text-white">
                <span className="block text-white/95">The Future Of</span>
                <span className="block text-white/95">Buying</span>
                <span className="block text-white/95">Starts With</span>
                <span className="block text-transparent bg-clip-text bg-gradient-to-r from-[#ff1695] via-pink-500 to-rose-400 font-extrabold italic tracking-normal drop-shadow-[0_0_35px_rgba(255,22,149,0.35)]">
                  INTELLIGENCE.
                </span>
              </h1>

              {/* Supporting Copy - Short Editorial Rhythm */}
              <p className="mt-5 sm:mt-8 text-sm sm:text-lg lg:text-xl text-white/60 font-light tracking-tight max-w-xl leading-relaxed">
                Compare less. Decide smarter. Real-time spec aggregation, authenticated price tracking, and unbiased AI recommendations.
              </p>

              {/* Dual Action CTAs - Touch Friendly */}
              <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3.5 sm:gap-6 mt-8 sm:mt-10">
                {/* Primary CTA */}
                <Link
                  href="/compare"
                  className="group relative inline-flex items-center justify-center px-8 py-4 min-h-[48px] bg-[#ff1695] hover:bg-[#e00d7f] text-white font-medium text-sm tracking-wide rounded-full overflow-hidden transition-all duration-300 shadow-[0_0_30px_rgba(255,22,149,0.4)] hover:shadow-[0_0_45px_rgba(255,22,149,0.6)] hover:scale-[1.02] active:scale-[0.98] w-full sm:w-auto"
                >
                  <span className="relative z-10 flex items-center justify-center gap-3">
                    <span>Start Live Comparison</span>
                    <ArrowRight className="w-4 h-4 transition-transform duration-300 group-hover:translate-x-1" />
                  </span>
                  <div className="absolute inset-0 -translate-x-full group-hover:translate-x-full transition-transform duration-1000 bg-gradient-to-r from-transparent via-white/20 to-transparent" />
                </Link>

                {/* Secondary CTA */}
                <Link
                  href="/search"
                  className="group inline-flex items-center justify-center px-8 py-4 min-h-[48px] bg-white/[0.03] hover:bg-white/[0.08] border border-white/15 hover:border-white/30 text-white/90 hover:text-white font-medium text-sm tracking-wide rounded-full backdrop-blur-md transition-all duration-300 hover:scale-[1.02] active:scale-[0.98] w-full sm:w-auto"
                >
                  <span className="flex items-center justify-center gap-2.5">
                    <Sparkles className="w-4 h-4 text-[#ff1695] group-hover:rotate-12 transition-transform duration-300" />
                    <span>Explore Catalog</span>
                  </span>
                </Link>
              </div>

              {/* Micro Metrics Strip */}
              <div className="grid grid-cols-3 gap-4 sm:gap-6 pt-8 sm:pt-10 mt-8 sm:mt-10 border-t border-white/10 max-w-lg">
                <div>
                  <div className="text-lg sm:text-2xl font-bold font-mono text-white">1K+</div>
                  <div className="text-[0.65rem] sm:text-xs text-white/50 tracking-wider uppercase mt-1">Comparisons</div>
                </div>
                <div>
                  <div className="text-lg sm:text-2xl font-bold font-mono text-white">99.8%</div>
                  <div className="text-[0.65rem] sm:text-xs text-white/50 tracking-wider uppercase mt-1">Accuracy</div>
                </div>
                <div>
                  <div className="text-lg sm:text-2xl font-bold font-mono text-[#ff1695]">$0</div>
                  <div className="text-[0.65rem] sm:text-xs text-white/50 tracking-wider uppercase mt-1">Sponsored Bias</div>
                </div>
              </div>
            </motion.div>
          </div>

          {/* ── RIGHT: FLOATING 3D GLASS SHOWCASE ── */}
          <div className="col-span-12 lg:col-span-5 relative mt-10 lg:mt-0 flex justify-center">
            <motion.div
              initial={{ opacity: 0, scale: 0.94, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              transition={{ duration: 1, delay: 0.2, ease: [0.16, 1, 0.3, 1] }}
              className="relative w-full max-w-md lg:max-w-none"
            >
              {/* Ambient Floating Box Animation Wrapper */}
              <motion.div
                animate={{ y: [0, -10, 0] }}
                transition={{ duration: 6, repeat: Infinity, ease: 'easeInOut' }}
                className="relative rounded-3xl bg-gradient-to-b from-white/10 to-white/[0.02] p-5 sm:p-8 border border-white/15 backdrop-blur-2xl shadow-[0_32px_64px_-16px_rgba(0,0,0,0.9)] overflow-hidden group"
              >
                {/* Glass Reflection */}
                <div className="absolute -top-[100%] left-0 right-0 h-[200%] bg-gradient-to-b from-white/10 via-transparent to-transparent rotate-45 pointer-events-none opacity-40 group-hover:opacity-70 transition-opacity" />

                {/* Top Bar inside Card */}
                <div className="flex items-center justify-between pb-4 sm:pb-5 border-b border-white/10">
                  <div className="flex items-center gap-2">
                    <Cpu className="w-4 h-4 text-[#ff1695]" />
                    <span className="text-[0.65rem] sm:text-xs font-mono tracking-widest text-white/80 uppercase">AI MATCH MATCHUP</span>
                  </div>
                  <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-[#ff1695]/10 border border-[#ff1695]/20 text-[#ff1695] text-[0.65rem] sm:text-xs font-mono">
                    <ShieldCheck className="w-3.5 h-3.5" />
                    <span>VERIFIED</span>
                  </div>
                </div>

                {/* Product Side-by-Side Visuals */}
                <div className="grid grid-cols-2 gap-3 sm:gap-4 my-4 sm:my-6 relative">
                  {/* Product A */}
                  <div className="relative rounded-2xl bg-white/[0.03] border border-white/10 p-3 sm:p-4 flex flex-col items-center text-center">
                    <div className="absolute top-2 left-2 sm:top-3 sm:left-3 text-[0.6rem] sm:text-[0.65rem] font-mono uppercase bg-white/10 px-2 py-0.5 rounded text-white/80">
                      Top Match
                    </div>
                    <div className="w-20 h-20 sm:w-28 sm:h-28 my-2 sm:my-3 flex items-center justify-center relative">
                      <img
                        src={heroProduct.image}
                        alt={heroProduct.name}
                        className="max-h-full max-w-full object-contain filter drop-shadow-[0_12px_24px_rgba(0,0,0,0.8)] group-hover:scale-105 transition-transform duration-700"
                      />
                    </div>
                    <h4 className="text-[0.7rem] sm:text-xs font-medium text-white line-clamp-1">{heroProduct.name}</h4>
                    <p className="text-[0.65rem] sm:text-[0.7rem] font-mono text-[#ff1695] font-semibold mt-1">
                      {formatPrice(heroProduct.bestPrice)}
                    </p>
                  </div>

                  {/* Versus Badge Divider */}
                  <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-7 h-7 sm:w-8 sm:h-8 rounded-full bg-[#ff1695] border border-white/30 flex items-center justify-center text-[0.6rem] sm:text-[0.65rem] font-black text-white shadow-lg z-10">
                    VS
                  </div>

                  {/* Product B */}
                  <div className="relative rounded-2xl bg-white/[0.03] border border-white/10 p-3 sm:p-4 flex flex-col items-center text-center">
                    <div className="w-20 h-20 sm:w-28 sm:h-28 my-2 sm:my-3 flex items-center justify-center relative">
                      <img
                        src={competitorProduct.image}
                        alt={competitorProduct.name}
                        className="max-h-full max-w-full object-contain filter drop-shadow-[0_12px_24px_rgba(0,0,0,0.8)] opacity-90 group-hover:scale-105 transition-transform duration-700"
                      />
                    </div>
                    <h4 className="text-[0.7rem] sm:text-xs font-medium text-white/80 line-clamp-1">{competitorProduct.name}</h4>
                    <p className="text-[0.65rem] sm:text-[0.7rem] font-mono text-white/60 mt-1">
                      {formatPrice(competitorProduct.bestPrice)}
                    </p>
                  </div>
                </div>

                {/* Score Bar */}
                <div className="space-y-2 pt-2">
                  <div className="flex justify-between text-[0.7rem] sm:text-xs font-mono">
                    <span className="text-white/70">AI Confidence Index</span>
                    <span className="text-[#ff1695] font-bold">98.4% Match</span>
                  </div>
                  <div className="h-2 w-full bg-white/10 rounded-full overflow-hidden p-0.5">
                    <div className="h-full bg-gradient-to-r from-[#ff1695] via-pink-500 to-rose-400 rounded-full w-[98%]" />
                  </div>
                </div>
              </motion.div>

              {/* Floating Live Badge 1: Price Drop */}
              <motion.div
                animate={{ y: [0, 6, 0] }}
                transition={{ duration: 5, repeat: Infinity, ease: 'easeInOut', delay: 1 }}
                className="absolute -bottom-4 sm:-bottom-6 -left-3 sm:-left-8 px-3 sm:px-4 py-2.5 sm:py-3 rounded-2xl bg-[#0d0d12]/95 border border-emerald-500/30 backdrop-blur-xl shadow-2xl flex items-center gap-2.5 sm:gap-3 z-20 max-w-[200px] sm:max-w-none"
              >
                <div className="w-7 h-7 sm:w-9 sm:h-9 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400 shrink-0">
                  <TrendingDown className="w-4 h-4 sm:w-5 sm:h-5" />
                </div>
                <div>
                  <div className="text-[0.6rem] sm:text-[0.65rem] font-mono uppercase tracking-wider text-emerald-400 font-semibold">
                    Price Alert
                  </div>
                  <div className="text-[0.7rem] sm:text-xs font-medium text-white line-clamp-1">
                    Save 25% on XM5
                  </div>
                </div>
              </motion.div>

              {/* Floating Live Badge 2: AI Verdict */}
              <motion.div
                animate={{ y: [0, -6, 0] }}
                transition={{ duration: 5.5, repeat: Infinity, ease: 'easeInOut', delay: 0.5 }}
                className="absolute -top-4 sm:-top-6 -right-3 sm:-right-6 px-3 sm:px-4 py-2.5 sm:py-3 rounded-2xl bg-[#0d0d12]/95 border border-[#ff1695]/30 backdrop-blur-xl shadow-2xl flex items-center gap-2.5 sm:gap-3 z-20 max-w-[200px] sm:max-w-none"
              >
                <div className="w-7 h-7 sm:w-9 sm:h-9 rounded-xl bg-[#ff1695]/10 border border-[#ff1695]/20 flex items-center justify-center text-[#ff1695] shrink-0">
                  <CheckCircle2 className="w-4 h-4 sm:w-5 sm:h-5" />
                </div>
                <div>
                  <div className="text-[0.6rem] sm:text-[0.65rem] font-mono uppercase tracking-wider text-[#ff1695] font-semibold">
                    Zero Sponsored Bias
                  </div>
                  <div className="text-[0.7rem] sm:text-xs font-medium text-white line-clamp-1">
                    100% Algorithmic Truth
                  </div>
                </div>
              </motion.div>
            </motion.div>
          </div>

        </div>
      </div>
    </section>
  )
}

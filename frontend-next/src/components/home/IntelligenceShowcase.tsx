'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import Link from 'next/link'
import { ArrowRight, Cpu, Zap, Check, ShieldCheck, BarChart3, Sliders } from 'lucide-react'
import { formatPrice } from '@/data/demoData'

const CATEGORY_SHOWCASES = [
  {
    id: 'headphones',
    name: 'Flagship Headphones',
    prodA: {
      id: 1,
      name: 'Sony WH-1000XM5',
      brand: 'Sony',
      price: 299.99,
      score: 96,
      image: 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?q=80&w=800&auto=format&fit=crop',
      anc: '30dB Hybrid ANC',
      battery: '30 Hours',
      weight: '250g',
      driver: '30mm Carbon Fiber',
    },
    prodB: {
      id: 2,
      name: 'Bose QuietComfort Ultra',
      brand: 'Bose',
      price: 379.00,
      score: 92,
      image: 'https://images.unsplash.com/photo-1546435770-a3e426bf472b?q=80&w=800&auto=format&fit=crop',
      anc: '28dB Active ANC',
      battery: '24 Hours',
      weight: '254g',
      driver: '35mm Dynamic',
    },
    verdict: 'Sony XM5 leads in ANC attenuation (-30dB) and battery endurance (+6h), making it the optimal value pick.',
    winnerId: 1,
  },
  {
    id: 'smartphones',
    name: 'Pro Smartphones',
    prodA: {
      id: 10,
      name: 'Samsung Galaxy S24 Ultra',
      brand: 'Samsung',
      price: 1199.99,
      score: 95,
      image: 'https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?q=80&w=800&auto=format&fit=crop',
      anc: 'Snapdragon 8 Gen 3',
      battery: '5000 mAh',
      weight: '232g',
      driver: '200MP Main + 5x Tele',
    },
    prodB: {
      id: 11,
      name: 'iPhone 15 Pro Max',
      brand: 'Apple',
      price: 1199.00,
      score: 94,
      image: 'https://images.unsplash.com/photo-1510557880182-3d4d3cba35a5?q=80&w=800&auto=format&fit=crop',
      anc: 'Apple A17 Pro 3nm',
      battery: '4422 mAh',
      weight: '221g',
      driver: '48MP Main + 5x Tetraprism',
    },
    verdict: 'Galaxy S24 Ultra edges out in zoom resolution & display peak brightness (2600 nits), while iPhone offers superior ProRes video.',
    winnerId: 10,
  },
  {
    id: 'laptops',
    name: 'Workstation Laptops',
    prodA: {
      id: 20,
      name: 'MacBook Pro 16" M3 Max',
      brand: 'Apple',
      price: 3499.00,
      score: 98,
      image: 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?q=80&w=800&auto=format&fit=crop',
      anc: '16-Core CPU / 40-Core GPU',
      battery: '22 Hours',
      weight: '2.14kg',
      driver: '16.2" Liquid Retina XDR',
    },
    prodB: {
      id: 21,
      name: 'Dell XPS 16 (i9 / RTX 4070)',
      brand: 'Dell',
      price: 2999.99,
      score: 89,
      image: 'https://images.unsplash.com/photo-1593642632823-8f785ba67e45?q=80&w=800&auto=format&fit=crop',
      anc: 'Core Ultra 9 / RTX 4070',
      battery: '12 Hours',
      weight: '2.20kg',
      driver: '16.3" 4K+ OLED Touch',
    },
    verdict: 'MacBook Pro M3 Max dominates sustained thermal efficiency and battery life by a 1.8x margin.',
    winnerId: 20,
  },
]

export default function IntelligenceShowcase() {
  const [activeTab, setActiveTab] = useState('headphones')

  const currentShowcase = CATEGORY_SHOWCASES.find((item) => item.id === activeTab) || CATEGORY_SHOWCASES[0]

  return (
    <section className="relative py-20 sm:py-28 bg-[#09090d] text-white overflow-hidden border-b border-white/10">
      {/* Soft Background Ambient Light */}
      <div className="absolute top-1/2 left-0 w-96 h-96 bg-[#ff1695]/10 blur-[130px] rounded-full pointer-events-none" />

      <div className="w-full max-w-[1536px] mx-auto px-4 sm:px-10 lg:px-16">
        
        {/* Chapter Header */}
        <div className="flex flex-col md:flex-row md:items-end justify-between mb-12 sm:mb-16 gap-6">
          <div>
            <div className="flex items-center gap-2 mb-3">
              <span className="text-[#ff1695] font-mono text-xs tracking-widest font-semibold uppercase">
                CHAPTER 01
              </span>
              <span className="text-white/30 text-xs">/</span>
              <span className="text-white/60 font-mono text-xs tracking-widest uppercase">
                INTELLIGENCE
              </span>
            </div>
            <h2 className="text-3xl sm:text-4xl md:text-5xl font-[var(--font-display)] font-semibold tracking-tight uppercase max-w-2xl leading-tight">
              We Strip Away The <span className="text-[#ff1695] italic">Marketing Noise.</span>
            </h2>
          </div>
          <p className="text-white/60 text-sm sm:text-base max-w-md font-light leading-relaxed">
            Our AI engine ingests real specifications, benchmarks, and multi-retailer reviews to calculate true hardware value.
          </p>
        </div>

        {/* Category Selector Tabs */}
        <div className="flex items-center gap-2.5 sm:gap-3 overflow-x-auto pb-4 mb-8 sm:mb-12 hide-scrollbar">
          {CATEGORY_SHOWCASES.map((category) => {
            const isActive = category.id === activeTab
            return (
              <button
                key={category.id}
                onClick={() => setActiveTab(category.id)}
                className={`relative px-4 sm:px-6 py-2.5 sm:py-3 rounded-full text-xs font-mono tracking-wider uppercase transition-all duration-300 whitespace-nowrap min-h-[44px] ${
                  isActive
                    ? 'bg-[#ff1695] text-white font-bold shadow-[0_0_20px_rgba(255,22,149,0.4)]'
                    : 'bg-white/[0.04] text-white/60 hover:text-white hover:bg-white/[0.08] border border-white/10'
                }`}
              >
                {category.name}
              </button>
            )
          })}
        </div>

        {/* Interactive Match Breakdown Box */}
        <AnimatePresence mode="wait">
          <motion.div
            key={activeTab}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
            className="rounded-3xl bg-gradient-to-b from-white/[0.05] to-white/[0.01] border border-white/15 p-4 sm:p-6 lg:p-10 backdrop-blur-xl shadow-2xl relative w-full max-w-full overflow-hidden"
          >
            <div className="grid grid-cols-12 gap-6 lg:gap-8 items-center">
              
              {/* Product A Card */}
              <div className="col-span-12 lg:col-span-5 relative rounded-2xl bg-white/[0.03] border border-white/10 p-4 sm:p-6 flex flex-col justify-between h-full w-full max-w-full overflow-hidden">
                {/* AI Verdict Badge - Mobile Safe Anchoring */}
                {currentShowcase.prodA.id === currentShowcase.winnerId && (
                  <div className="absolute top-3 right-3 sm:top-4 sm:right-4 flex items-center gap-1 sm:gap-1.5 px-2 sm:px-3 py-0.5 sm:py-1 rounded-full bg-[#ff1695]/20 border border-[#ff1695]/40 text-[#ff1695] text-[0.6rem] sm:text-xs font-mono font-bold shrink z-10">
                    <ShieldCheck className="w-3 h-3 sm:w-3.5 sm:h-3.5 shrink-0" />
                    <span className="truncate">AI VERDICT WINNER</span>
                  </div>
                )}

                {/* Header: Left Aligned Image & Natural Text Stack */}
                <div className="flex items-center gap-3 sm:gap-6 pt-5 sm:pt-0">
                  <div className="w-16 h-16 sm:w-28 sm:h-28 shrink-0 bg-white/[0.03] rounded-xl p-2 sm:p-3 flex items-center justify-center">
                    <img
                      src={currentShowcase.prodA.image}
                      alt={currentShowcase.prodA.name}
                      className="max-h-full max-w-full object-contain filter drop-shadow-xl"
                    />
                  </div>
                  <div className="min-w-0 flex-1">
                    <span className="text-[0.65rem] sm:text-[0.7rem] font-mono uppercase tracking-widest text-white/50 block">
                      {currentShowcase.prodA.brand}
                    </span>
                    <h3 className="text-sm sm:text-lg font-bold text-white mt-0.5 sm:mt-1 leading-snug line-clamp-2 break-words">
                      {currentShowcase.prodA.name}
                    </h3>
                    <div className="text-sm sm:text-base font-mono font-semibold text-[#ff1695] mt-1 sm:mt-2">
                      {formatPrice(currentShowcase.prodA.price)}
                    </div>
                  </div>
                </div>

                {/* Score & Specs */}
                <div className="mt-4 sm:mt-6 pt-4 sm:pt-6 border-t border-white/10 space-y-2.5 sm:space-y-3">
                  <div className="flex justify-between items-center text-[0.65rem] sm:text-xs font-mono">
                    <span className="text-white/60">Hardware Score</span>
                    <span className="text-white font-bold">{currentShowcase.prodA.score} / 100</span>
                  </div>
                  <div className="h-1.5 w-full max-w-full bg-white/10 rounded-full overflow-hidden">
                    <div
                      className="h-full max-w-full bg-gradient-to-r from-[#ff1695] to-rose-400 rounded-full"
                      style={{ width: `${currentShowcase.prodA.score}%` }}
                    />
                  </div>

                  {/* Feature Chips - Equal Heights & Touch Target */}
                  <div className="grid grid-cols-3 gap-1.5 sm:gap-2 pt-2 sm:pt-3 text-[0.65rem] sm:text-[0.7rem] font-mono text-white/70">
                    <div className="bg-white/[0.04] p-2 rounded text-center min-h-[44px] flex flex-col justify-center">
                      <div className="text-white/40 uppercase text-[0.55rem] sm:text-[0.6rem] tracking-wider truncate">Proc / ANC</div>
                      <div className="font-semibold text-white mt-0.5 line-clamp-1 truncate text-[0.65rem] sm:text-[0.7rem]">{currentShowcase.prodA.anc}</div>
                    </div>
                    <div className="bg-white/[0.04] p-2 rounded text-center min-h-[44px] flex flex-col justify-center">
                      <div className="text-white/40 uppercase text-[0.55rem] sm:text-[0.6rem] tracking-wider truncate">Battery</div>
                      <div className="font-semibold text-white mt-0.5 line-clamp-1 truncate text-[0.65rem] sm:text-[0.7rem]">{currentShowcase.prodA.battery}</div>
                    </div>
                    <div className="bg-white/[0.04] p-2 rounded text-center min-h-[44px] flex flex-col justify-center">
                      <div className="text-white/40 uppercase text-[0.55rem] sm:text-[0.6rem] tracking-wider truncate">Weight</div>
                      <div className="font-semibold text-white mt-0.5 line-clamp-1 truncate text-[0.65rem] sm:text-[0.7rem]">{currentShowcase.prodA.weight}</div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Central AI Verdict & VS Divider */}
              <div className="col-span-12 lg:col-span-2 flex flex-col items-center justify-center text-center my-2 sm:my-4 lg:my-0">
                <div className="w-8 h-8 sm:w-12 sm:h-12 rounded-full bg-[#ff1695] border border-white/30 flex items-center justify-center text-white font-black text-[0.65rem] sm:text-xs shadow-lg mb-2 sm:mb-4 shrink-0">
                  VS
                </div>
                <div className="p-3.5 sm:p-4 rounded-2xl bg-white/[0.03] border border-white/10 text-left w-full max-w-full">
                  <div className="flex items-center gap-1.5 text-xs font-mono font-bold text-[#ff1695] mb-1">
                    <Zap className="w-3.5 h-3.5 shrink-0" />
                    <span>AI SUMMARY</span>
                  </div>
                  <p className="text-xs text-white/80 font-light leading-relaxed break-words whitespace-normal">
                    {currentShowcase.verdict}
                  </p>
                </div>
              </div>

              {/* Product B Card */}
              <div className="col-span-12 lg:col-span-5 relative rounded-2xl bg-white/[0.03] border border-white/10 p-4 sm:p-6 flex flex-col justify-between h-full w-full max-w-full overflow-hidden">
                {currentShowcase.prodB.id === currentShowcase.winnerId && (
                  <div className="absolute top-3 right-3 sm:top-4 sm:right-4 flex items-center gap-1 sm:gap-1.5 px-2 sm:px-3 py-0.5 sm:py-1 rounded-full bg-[#ff1695]/20 border border-[#ff1695]/40 text-[#ff1695] text-[0.6rem] sm:text-xs font-mono font-bold shrink z-10">
                    <ShieldCheck className="w-3 h-3 sm:w-3.5 sm:h-3.5 shrink-0" />
                    <span className="truncate">AI VERDICT WINNER</span>
                  </div>
                )}

                <div className="flex items-center gap-3 sm:gap-6 pt-5 sm:pt-0">
                  <div className="w-16 h-16 sm:w-28 sm:h-28 shrink-0 bg-white/[0.03] rounded-xl p-2 sm:p-3 flex items-center justify-center">
                    <img
                      src={currentShowcase.prodB.image}
                      alt={currentShowcase.prodB.name}
                      className="max-h-full max-w-full object-contain filter drop-shadow-xl"
                    />
                  </div>
                  <div className="min-w-0 flex-1">
                    <span className="text-[0.65rem] sm:text-[0.7rem] font-mono uppercase tracking-widest text-white/50 block">
                      {currentShowcase.prodB.brand}
                    </span>
                    <h3 className="text-sm sm:text-lg font-bold text-white mt-0.5 sm:mt-1 leading-snug line-clamp-2 break-words">
                      {currentShowcase.prodB.name}
                    </h3>
                    <div className="text-sm sm:text-base font-mono font-semibold text-white/70 mt-1 sm:mt-2">
                      {formatPrice(currentShowcase.prodB.price)}
                    </div>
                  </div>
                </div>

                {/* Score & Specs */}
                <div className="mt-4 sm:mt-6 pt-4 sm:pt-6 border-t border-white/10 space-y-2.5 sm:space-y-3">
                  <div className="flex justify-between items-center text-[0.65rem] sm:text-xs font-mono">
                    <span className="text-white/60">Hardware Score</span>
                    <span className="text-white font-bold">{currentShowcase.prodB.score} / 100</span>
                  </div>
                  <div className="h-1.5 w-full max-w-full bg-white/10 rounded-full overflow-hidden">
                    <div
                      className="h-full max-w-full bg-white/40 rounded-full"
                      style={{ width: `${currentShowcase.prodB.score}%` }}
                    />
                  </div>

                  {/* Feature Chips - Equal Heights & Touch Target */}
                  <div className="grid grid-cols-3 gap-1.5 sm:gap-2 pt-2 sm:pt-3 text-[0.65rem] sm:text-[0.7rem] font-mono text-white/70">
                    <div className="bg-white/[0.04] p-2 rounded text-center min-h-[44px] flex flex-col justify-center">
                      <div className="text-white/40 uppercase text-[0.55rem] sm:text-[0.6rem] tracking-wider truncate">Proc / ANC</div>
                      <div className="font-semibold text-white mt-0.5 line-clamp-1 truncate text-[0.65rem] sm:text-[0.7rem]">{currentShowcase.prodB.anc}</div>
                    </div>
                    <div className="bg-white/[0.04] p-2 rounded text-center min-h-[44px] flex flex-col justify-center">
                      <div className="text-white/40 uppercase text-[0.55rem] sm:text-[0.6rem] tracking-wider truncate">Battery</div>
                      <div className="font-semibold text-white mt-0.5 line-clamp-1 truncate text-[0.65rem] sm:text-[0.7rem]">{currentShowcase.prodB.battery}</div>
                    </div>
                    <div className="bg-white/[0.04] p-2 rounded text-center min-h-[44px] flex flex-col justify-center">
                      <div className="text-white/40 uppercase text-[0.55rem] sm:text-[0.6rem] tracking-wider truncate">Weight</div>
                      <div className="font-semibold text-white mt-0.5 line-clamp-1 truncate text-[0.65rem] sm:text-[0.7rem]">{currentShowcase.prodB.weight}</div>
                    </div>
                  </div>
                </div>
              </div>

            </div>

            {/* Bottom CTA to Full Comparison Page */}
            <div className="mt-6 sm:mt-8 pt-4 sm:pt-6 border-t border-white/10 flex flex-col sm:flex-row items-center justify-between gap-3 sm:gap-4">
              <span className="text-[0.65rem] sm:text-xs text-white/50 font-mono text-center sm:text-left">
                ✦ Evaluated across 48 technical specs & 12,000+ customer reviews.
              </span>
              <Link
                href="/compare"
                className="inline-flex items-center gap-2 text-xs font-mono uppercase tracking-wider text-[#ff1695] hover:text-[#e00d7f] font-bold transition-colors group min-h-[44px]"
              >
                <span>Launch Full Comparison Engine</span>
                <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-1" />
              </Link>
            </div>
          </motion.div>
        </AnimatePresence>

      </div>
    </section>
  )
}

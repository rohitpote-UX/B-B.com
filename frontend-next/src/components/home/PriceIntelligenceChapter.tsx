'use client'

import { motion } from 'framer-motion'
import Link from 'next/link'
import { TrendingDown, ShieldAlert, ArrowRight, CheckCircle2, ShoppingCart, Tag } from 'lucide-react'
import { formatPrice } from '@/data/demoData'

const RETAILERS = [
  { name: 'Amazon', price: 299.99, isLowest: true, inStock: true },
  { name: 'Reliance Digital', price: 319.00, isLowest: false, inStock: true },
  { name: 'Flipkart', price: 324.50, isLowest: false, inStock: true },
  { name: 'Croma', price: 339.99, isLowest: false, inStock: false },
]

export default function PriceIntelligenceChapter() {
  return (
    <section className="relative py-28 bg-[#07070b] text-white overflow-hidden border-b border-white/10">
      {/* Glow Ambient background */}
      <div className="absolute bottom-10 left-1/3 w-[700px] h-[500px] bg-[#ff1695]/10 blur-[150px] rounded-full pointer-events-none" />

      <div className="w-full max-w-[1536px] mx-auto px-6 sm:px-10 lg:px-16 relative z-10">
        
        {/* Chapter Header */}
        <div className="flex flex-col md:flex-row md:items-end justify-between mb-16 gap-6">
          <div>
            <div className="flex items-center gap-2 mb-3">
              <span className="text-[#ff1695] font-mono text-xs tracking-widest font-semibold uppercase">
                CHAPTER 03
              </span>
              <span className="text-white/30 text-xs">/</span>
              <span className="text-white/60 font-mono text-xs tracking-widest uppercase">
                PRICE INTELLIGENCE
              </span>
            </div>
            <h2 className="text-3xl sm:text-4xl md:text-5xl font-[var(--font-display)] font-semibold tracking-tight uppercase leading-tight">
              Never Buy A <span className="text-[#ff1695] italic">Fake Discount</span> Again.
            </h2>
          </div>
          <p className="text-white/60 text-sm sm:text-base max-w-md font-light leading-relaxed">
            Many e-commerce sales boost original list prices right before applying a discount. Our 90-day price history algorithm exposes the true lowest price.
          </p>
        </div>

        {/* Price Tracking Interactive Card */}
        <div className="grid grid-cols-12 gap-8 items-stretch">
          
          {/* LEFT: 90-DAY PRICE HISTORY SVG CHART */}
          <div className="col-span-12 lg:col-span-7 rounded-3xl bg-white/[0.02] border border-white/15 p-6 sm:p-8 backdrop-blur-2xl flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between pb-6 border-b border-white/10">
                <div>
                  <h3 className="text-base font-bold text-white">Sony WH-1000XM5 Price Trajectory</h3>
                  <p className="text-xs text-white/50 font-mono mt-0.5">90-Day Cross-Platform Aggregation</p>
                </div>
                <div className="px-3 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-mono font-bold flex items-center gap-1.5">
                  <TrendingDown className="w-3.5 h-3.5" />
                  <span>25% BELOW 90-DAY AVG</span>
                </div>
              </div>

              {/* Interactive SVG Sparkline */}
              <div className="relative my-8 h-48 w-full flex flex-col justify-end">
                {/* SVG Curve */}
                <svg className="w-full h-full overflow-visible" viewBox="0 0 500 150" preserveAspectRatio="none">
                  {/* Gradient fill underneath */}
                  <defs>
                    <linearGradient id="priceGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#ff1695" stopOpacity="0.4" />
                      <stop offset="100%" stopColor="#ff1695" stopOpacity="0" />
                    </linearGradient>
                  </defs>

                  <path
                    d="M 0 40 Q 75 10, 150 90 T 300 30 T 420 120 T 500 130 L 500 150 L 0 150 Z"
                    fill="url(#priceGrad)"
                  />
                  <path
                    d="M 0 40 Q 75 10, 150 90 T 300 30 T 420 120 T 500 130"
                    fill="none"
                    stroke="#ff1695"
                    strokeWidth="3"
                    strokeLinecap="round"
                  />

                  {/* Lowest Point Pulsing Marker */}
                  <circle cx="500" cy="130" r="6" fill="#ff1695" className="animate-ping opacity-75" />
                  <circle cx="500" cy="130" r="5" fill="#ffffff" stroke="#ff1695" strokeWidth="2" />
                </svg>

                {/* Grid baseline labels */}
                <div className="flex justify-between items-center text-[0.7rem] font-mono text-white/40 pt-4 border-t border-white/10">
                  <span>90 Days Ago ($399)</span>
                  <span>60 Days Ago ($349)</span>
                  <span>30 Days Ago ($329)</span>
                  <span className="text-emerald-400 font-bold">Today ($299)</span>
                </div>
              </div>
            </div>

            {/* Deal Authentication Banner */}
            <div className="p-4 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0" />
                <div>
                  <h4 className="text-xs font-mono font-bold text-emerald-400 uppercase">
                    AUTHENTIC DEAL VERIFIED (SCORE: 94/100)
                  </h4>
                  <p className="text-xs text-white/70 font-light mt-0.5">
                    This price is within $5 of all-time lowest recorded price.
                  </p>
                </div>
              </div>
              <Link
                href="/deals"
                className="hidden sm:inline-flex items-center gap-1.5 text-xs font-mono text-emerald-400 hover:text-emerald-300 font-bold"
              >
                <span>View Deals</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>
          </div>

          {/* RIGHT: MULTI-RETAILER LIVE COMPARISON */}
          <div className="col-span-12 lg:col-span-5 rounded-3xl bg-white/[0.02] border border-white/15 p-6 sm:p-8 backdrop-blur-2xl flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between pb-4 border-b border-white/10 mb-6">
                <div className="flex items-center gap-2">
                  <Tag className="w-4 h-4 text-[#ff1695]" />
                  <span className="text-xs font-mono tracking-widest uppercase text-white/80">
                    LIVE RETAILER MATRIX
                  </span>
                </div>
                <span className="text-[0.65rem] font-mono text-white/50">UPDATED 2 MINS AGO</span>
              </div>

              {/* Retailer Price List */}
              <div className="space-y-3.5">
                {RETAILERS.map((r) => (
                  <div
                    key={r.name}
                    className={`p-3.5 rounded-xl border transition-all duration-300 flex items-center justify-between ${
                      r.isLowest
                        ? 'bg-[#ff1695]/10 border-[#ff1695]/40 shadow-[0_0_20px_rgba(255,22,149,0.15)]'
                        : 'bg-white/[0.02] border-white/[0.06]'
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-lg bg-white/10 flex items-center justify-center text-xs font-bold text-white">
                        {r.name[0]}
                      </div>
                      <div>
                        <h5 className="text-xs font-medium text-white">{r.name}</h5>
                        <p className="text-[0.65rem] font-mono text-white/50">
                          {r.inStock ? 'In Stock • Free Delivery' : 'Out of Stock'}
                        </p>
                      </div>
                    </div>

                    <div className="text-right">
                      <div
                        className={`text-sm font-mono font-bold ${
                          r.isLowest ? 'text-emerald-400' : 'text-white/80'
                        }`}
                      >
                        {formatPrice(r.price)}
                      </div>
                      {r.isLowest && (
                        <span className="text-[0.6rem] font-mono uppercase bg-emerald-500/20 text-emerald-400 px-1.5 py-0.5 rounded font-bold">
                          Best Offer
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="mt-6 pt-4 border-t border-white/10 flex justify-between items-center">
              <span className="text-xs font-mono text-white/50">Tracking 1,460+ Products</span>
              <Link
                href="/deals"
                className="inline-flex items-center justify-center px-5 py-2.5 rounded-full bg-white/10 hover:bg-white/20 text-white text-xs font-mono tracking-wider uppercase transition-colors"
              >
                Market Watch Dashboard
              </Link>
            </div>
          </div>

        </div>

      </div>
    </section>
  )
}

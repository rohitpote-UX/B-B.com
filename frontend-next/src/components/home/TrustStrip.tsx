'use client'

import { motion } from 'framer-motion'
import { Cpu, RefreshCw, Layers, ShoppingBag, ShieldAlert, Sparkles } from 'lucide-react'

const TRUST_ITEMS = [
  {
    icon: Cpu,
    label: 'AI-POWERED MATCHING',
    subtext: 'Neural knowledge graph',
  },
  {
    icon: RefreshCw,
    label: 'REAL-TIME PRICES',
    subtext: 'Cross-platform sync',
  },
  {
    icon: Layers,
    label: '1,000+ COMPARISONS',
    subtext: '50+ hardware vectors',
  },
  {
    icon: ShoppingBag,
    label: 'MULTI-RETAILER TRUTH',
    subtext: 'Amazon, Flipkart, Croma',
  },
  {
    icon: ShieldAlert,
    label: 'ZERO SPONSORED RANKINGS',
    subtext: 'Strict algorithm autonomy',
  },
  {
    icon: Sparkles,
    label: 'EXPLAINABLE AI',
    subtext: 'Transparent match scores',
  },
]

export default function TrustStrip() {
  return (
    <section className="relative py-8 sm:py-10 bg-[#07070a] border-y border-white/10 overflow-hidden">
      {/* Background ambient lighting */}
      <div className="absolute inset-0 bg-gradient-to-r from-[#ff1695]/[0.03] via-transparent to-[#ff1695]/[0.03] pointer-events-none" />

      <div className="w-full max-w-[1536px] mx-auto px-4 sm:px-8 md:px-12 lg:px-16">
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 sm:gap-6 lg:gap-8 items-center">
          {TRUST_ITEMS.map((item, idx) => {
            const IconComponent = item.icon
            return (
              <motion.div
                key={item.label}
                initial={{ opacity: 0, y: 15 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: idx * 0.08 }}
                className="group relative flex flex-col items-start p-3.5 sm:p-4 rounded-xl bg-white/[0.015] hover:bg-white/[0.04] border border-white/[0.05] hover:border-[#ff1695]/30 transition-all duration-300 backdrop-blur-sm min-h-[72px]"
              >
                <div className="flex items-center gap-2 sm:gap-3 mb-2">
                  <div className="p-1.5 sm:p-2 rounded-lg bg-[#ff1695]/10 text-[#ff1695] group-hover:bg-[#ff1695] group-hover:text-white transition-colors duration-300">
                    <IconComponent className="w-3.5 h-3.5 sm:w-4 sm:h-4" strokeWidth={1.5} />
                  </div>
                  <span className="relative flex h-1.5 w-1.5">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#ff1695] opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-1.5 w-1.5 bg-[#ff1695]"></span>
                  </span>
                </div>
                
                <h4 className="text-[0.65rem] sm:text-xs font-mono font-semibold tracking-wider text-white/90 group-hover:text-white transition-colors leading-tight">
                  {item.label}
                </h4>
                <p className="text-[0.65rem] text-white/50 font-light mt-0.5 line-clamp-1">
                  {item.subtext}
                </p>

                {/* Subtle border glow on hover */}
                <div className="absolute inset-0 rounded-xl bg-gradient-to-r from-[#ff1695]/0 via-[#ff1695]/10 to-[#ff1695]/0 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none" />
              </motion.div>
            )
          })}
        </div>
      </div>
    </section>
  )
}

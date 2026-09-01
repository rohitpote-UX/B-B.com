'use client'

import { motion } from 'framer-motion'
import { Check, SlidersHorizontal, Layers, Cpu, CheckCircle } from 'lucide-react'

const STANDARDIZATION_METRICS = [
  {
    category: 'Display & Optics',
    raw: '120Hz LTPO OLED / 2600 nits Peak',
    normalized: 'Peak Outdoor Legibility Score: 9.8/10',
    progress: 98,
  },
  {
    category: 'Sustained Thermal Performance',
    raw: 'AnTuTu v10: 1,850,000 pts (35% throttle)',
    normalized: 'True Continuous Workload Score: 88/100',
    progress: 88,
  },
  {
    category: 'Real-World Battery Endurance',
    raw: '5000 mAh / 45W Fast Charging',
    normalized: 'Screen-On-Time Standardized: 11.4 Hours',
    progress: 94,
  },
  {
    category: 'Build & Durability',
    raw: 'Titanium Frame / Armor Glass 2',
    normalized: 'Drop & Scratch Resistance Index: 9.5/10',
    progress: 95,
  },
]

export default function SpecComparisonChapter() {
  return (
    <section className="relative py-20 sm:py-28 bg-[#050505] text-white overflow-hidden border-b border-white/10">
      {/* Background radial highlight */}
      <div className="absolute top-1/3 right-1/4 w-[600px] h-[600px] bg-[#ff1695]/5 blur-[160px] rounded-full pointer-events-none" />

      <div className="w-full max-w-[1536px] mx-auto px-4 sm:px-10 lg:px-16 relative z-10">
        
        <div className="grid grid-cols-12 gap-8 lg:gap-16 items-center">
          
          {/* LEFT: EDITORIAL STORY */}
          <div className="col-span-12 lg:col-span-6">
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.8 }}
            >
              <div className="flex items-center gap-2 mb-4">
                <span className="text-[#ff1695] font-mono text-xs tracking-widest font-semibold uppercase">
                  CHAPTER 02
                </span>
                <span className="text-white/30 text-xs">/</span>
                <span className="text-white/60 font-mono text-xs tracking-widest uppercase">
                  SIDE-BY-SIDE PRECISION
                </span>
              </div>

              <h2 className="text-3xl sm:text-4xl lg:text-5xl font-[var(--font-display)] font-semibold tracking-tight uppercase leading-[1.05] text-white mb-6">
                50+ Hardware Metrics <span className="text-[#ff1695] italic">Standardized.</span> Zero Ambiguity.
              </h2>

              <p className="text-white/60 text-base lg:text-lg font-light leading-relaxed mb-8 max-w-xl">
                Brand spec sheets are intentionally designed to confuse. One brand advertises peak burst clock speed; another lists lab battery life under 10% screen brightness. We convert every technical parameter into a single, standardized matrix.
              </p>

              <div className="space-y-4 mb-10">
                {[
                  'Unified mathematical normalizers for cross-brand comparison',
                  'Thermal throttling penalties applied to synthetic benchmarks',
                  'Price-to-Performance curve updated in real-time',
                ].map((item, idx) => (
                  <div key={idx} className="flex items-start gap-3 text-sm text-white/80">
                    <div className="p-1 rounded bg-[#ff1695]/10 text-[#ff1695] shrink-0 mt-0.5">
                      <Check className="w-3.5 h-3.5" />
                    </div>
                    <span>{item}</span>
                  </div>
                ))}
              </div>
            </motion.div>
          </div>

          {/* RIGHT: LIVE SPEC MATRIX CARD */}
          <div className="col-span-12 lg:col-span-6">
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              transition={{ duration: 0.8 }}
              className="rounded-3xl bg-white/[0.02] border border-white/15 p-4 sm:p-6 lg:p-8 backdrop-blur-2xl shadow-2xl relative max-w-full overflow-hidden"
            >
              {/* Header */}
              <div className="flex items-center justify-between pb-4 sm:pb-6 border-b border-white/10 mb-4 sm:mb-6">
                <div className="flex items-center gap-2">
                  <SlidersHorizontal className="w-4 h-4 text-[#ff1695]" />
                  <span className="text-[0.65rem] sm:text-xs font-mono tracking-widest uppercase text-white/80">
                    NORMALIZATION PIPELINE
                  </span>
                </div>
                <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-[0.65rem] sm:text-[0.7rem] font-mono">
                  <CheckCircle className="w-3 h-3" />
                  <span>ACTIVE MATRIX</span>
                </div>
              </div>

              {/* Rows - Responsive Vertical Stack on Mobile (<768px) */}
              <div className="space-y-4 sm:space-y-6">
                {STANDARDIZATION_METRICS.map((metric, idx) => (
                  <div key={idx} className="p-3.5 sm:p-4 rounded-2xl bg-white/[0.02] border border-white/[0.06] space-y-2.5 max-w-full overflow-hidden">
                    <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-1 text-xs font-mono">
                      <span className="text-white/50 uppercase text-[0.65rem] sm:text-xs tracking-wider">{metric.category}</span>
                      <span className="text-[#ff1695] font-semibold break-words whitespace-normal leading-snug">{metric.normalized}</span>
                    </div>

                    <div className="text-xs text-white/80 font-light flex flex-col sm:flex-row sm:items-center sm:justify-between gap-0.5 sm:gap-2">
                      <span className="text-white/40 font-mono text-[0.65rem] sm:text-[0.7rem] shrink-0">Raw Spec:</span>
                      <span className="font-mono text-white/90 break-words whitespace-normal text-[0.7rem] sm:text-xs">{metric.raw}</span>
                    </div>

                    <div className="h-1.5 w-full max-w-full bg-white/10 rounded-full overflow-hidden">
                      <motion.div
                        initial={{ width: 0 }}
                        whileInView={{ width: `${metric.progress}%` }}
                        viewport={{ once: true }}
                        transition={{ duration: 1, delay: idx * 0.15 }}
                        className="h-full max-w-full bg-gradient-to-r from-[#ff1695] via-pink-500 to-rose-400 rounded-full"
                      />
                    </div>
                  </div>
                ))}
              </div>

              {/* Card Footer */}
              <div className="mt-4 sm:mt-6 pt-4 border-t border-white/10 flex justify-between items-center text-[0.65rem] sm:text-[0.7rem] font-mono text-white/40">
                <span>Data Source: Hardware Graph v4.8</span>
                <span>Latency: 14ms</span>
              </div>
            </motion.div>
          </div>

        </div>

      </div>
    </section>
  )
}

'use client'

import { motion } from 'framer-motion'
import Link from 'next/link'
import { ArrowRight, Sparkles, Cpu, ShieldCheck } from 'lucide-react'

export default function FinalCtaSection() {
  return (
    <section className="relative py-32 bg-[#050505] text-white overflow-hidden">
      {/* Radiant Glow Mesh */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[900px] h-[500px] bg-[#ff1695]/15 blur-[170px] rounded-full pointer-events-none" />
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(255,22,149,0.1)_0,transparent_70%)] pointer-events-none" />

      <div className="w-full max-w-[1536px] mx-auto px-6 sm:px-10 lg:px-16 relative z-10">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
          className="rounded-3xl bg-gradient-to-b from-white/[0.05] to-white/[0.01] border border-white/20 p-10 sm:p-16 text-center backdrop-blur-3xl shadow-[0_32px_64px_-16px_rgba(0,0,0,0.9)] relative overflow-hidden"
        >
          {/* Top Label */}
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-white/[0.04] border border-white/10 mb-8">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#ff1695] opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-[#ff1695]"></span>
            </span>
            <span className="text-xs font-mono tracking-widest uppercase text-white/80">
              CHAPTER 05 / DECISION CONFIDENCE
            </span>
          </div>

          {/* Massive Statement */}
          <h2 className="text-4xl sm:text-6xl md:text-7xl font-[var(--font-display)] font-semibold tracking-tight uppercase max-w-4xl mx-auto leading-[0.95] mb-6">
            Compare Less. <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#ff1695] via-pink-500 to-rose-400 font-extrabold italic drop-shadow-[0_0_40px_rgba(255,22,149,0.4)]">
              Decide Smarter.
            </span>
          </h2>

          <p className="text-base sm:text-xl text-white/60 font-light max-w-xl mx-auto mb-10 leading-relaxed">
            Join thousands of smart buyers using Brand Battle to make objective, data-driven hardware purchases every single day.
          </p>

          {/* Dual CTAs */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-5">
            <Link
              href="/compare"
              className="group relative inline-flex items-center justify-center px-9 py-4 bg-[#ff1695] hover:bg-[#e00d7f] text-white font-medium text-sm tracking-wide rounded-full overflow-hidden transition-all duration-300 shadow-[0_0_35px_rgba(255,22,149,0.5)] hover:shadow-[0_0_55px_rgba(255,22,149,0.7)] hover:scale-[1.03] active:scale-[0.97]"
            >
              <span className="relative z-10 flex items-center gap-3">
                <span>Start Live Comparison</span>
                <ArrowRight className="w-4 h-4 transition-transform duration-300 group-hover:translate-x-1" />
              </span>
              <div className="absolute inset-0 -translate-x-full group-hover:translate-x-full transition-transform duration-1000 bg-gradient-to-r from-transparent via-white/20 to-transparent" />
            </Link>

            <Link
              href="/advisor"
              className="inline-flex items-center justify-center px-8 py-4 bg-white/[0.04] hover:bg-white/[0.08] border border-white/15 hover:border-white/30 text-white font-medium text-sm tracking-wide rounded-full backdrop-blur-md transition-all duration-300 hover:scale-[1.02]"
            >
              <span className="flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-[#ff1695]" />
                <span>Launch AI Advisor</span>
              </span>
            </Link>
          </div>

          {/* Bottom Security Guarantee */}
          <div className="mt-12 pt-8 border-t border-white/10 flex items-center justify-center gap-6 text-xs font-mono text-white/50">
            <span className="flex items-center gap-1.5">
              <ShieldCheck className="w-4 h-4 text-[#ff1695]" />
              100% Unbiased Algorithm
            </span>
            <span>•</span>
            <span className="flex items-center gap-1.5">
              <Cpu className="w-4 h-4 text-[#ff1695]" />
              Instant Hardware Graph
            </span>
          </div>
        </motion.div>
      </div>
    </section>
  )
}

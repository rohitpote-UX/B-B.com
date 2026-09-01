'use client'

import React from 'react'
import Link from 'next/link'
import { motion } from 'framer-motion'
import { ShieldCheck, Sparkles, AlertTriangle, Eye, ArrowRight, Zap, Target } from 'lucide-react'

export default function ManifestoClient() {
  return (
    <div className="min-h-screen bg-[#050505] text-[#f4f4f5] font-sans antialiased selection:bg-[#f20ab0] selection:text-white">
      {/* Hero Header */}
      <section className="relative pt-24 pb-16 px-6 max-w-5xl mx-auto text-center border-b border-theme-border/50">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <span className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold uppercase tracking-widest bg-[#f20ab015] text-[#f20ab0] border border-[#f20ab030] mb-6">
            <Sparkles className="w-3.5 h-3.5" /> The Brand Battle Manifesto
          </span>
          <h1 className="text-4xl md:text-6xl font-extrabold tracking-tight text-white mb-6 leading-tight">
            Shopping Shouldn't Require <br className="hidden sm:inline" />
            <span className="bg-gradient-to-r from-white via-neutral-200 to-[#f20ab0] bg-clip-text text-transparent">
              Deception or Compromise.
            </span>
          </h1>
          <p className="text-lg md:text-xl text-[#a1a1aa] max-w-3xl mx-auto leading-relaxed">
            We built Brand Battle because e-commerce has lost its integrity. Here is why we exist, how modern shopping failed consumers, and how objective AI changes everything.
          </p>
        </motion.div>
      </section>

      <main className="max-w-4xl mx-auto px-6 py-16 space-y-24">
        {/* Section 1: The Problem */}
        <motion.section
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="space-y-6"
        >
          <div className="flex items-center gap-3 text-[#ef4444] font-bold text-xs uppercase tracking-widest">
            <AlertTriangle className="w-4 h-4" /> Section 01
          </div>
          <h2 className="text-2xl md:text-3xl font-extrabold text-white">
            The Problem: You Are Being Gamified
          </h2>
          <p className="text-[#a1a1aa] leading-relaxed text-base">
            Modern online shopping is no longer designed to help you find the best product. It is designed to maximize click-through rate, obscure true historical prices, and steer you toward high-margin items.
          </p>
          <div className="grid md:grid-cols-2 gap-4 pt-4">
            <div className="p-5 rounded-2xl bg-theme-elevated/40 border border-theme-border/60">
              <h3 className="font-bold text-white mb-2">Fake Discounts</h3>
              <p className="text-xs text-[#a1a1aa] leading-relaxed">
                Sticker prices are artificially inflated days before a sale so retailers can advertise fake "50% Off" deals that are actually full price.
              </p>
            </div>
            <div className="p-5 rounded-2xl bg-theme-elevated/40 border border-theme-border/60">
              <h3 className="font-bold text-white mb-2">Sponsored Search Pollution</h3>
              <p className="text-xs text-[#a1a1aa] leading-relaxed">
                The top 5 search results on major marketplaces are paid ad spots, regardless of product quality or seller reputation.
              </p>
            </div>
          </div>
        </motion.section>

        {/* Section 2: The Modern Shopping Crisis */}
        <motion.section
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="space-y-6 border-t border-theme-border/40 pt-16"
        >
          <div className="flex items-center gap-3 text-[#f20ab0] font-bold text-xs uppercase tracking-widest">
            <Eye className="w-4 h-4" /> Section 02
          </div>
          <h2 className="text-2xl md:text-3xl font-extrabold text-white">
            The Modern Shopping Crisis: Choice Fatigue
          </h2>
          <p className="text-[#a1a1aa] leading-relaxed text-base">
            With thousands of conflicting reviews, incentivized YouTube unboxings, and subtle affiliate bias, consumers spend hours researching simple purchases—and still end up with buyer's remorse.
          </p>
        </motion.section>

        {/* Section 3: Our Philosophy */}
        <motion.section
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="p-8 rounded-3xl bg-gradient-to-b from-[#f20ab008] to-transparent border border-[#f20ab025] space-y-6"
        >
          <div className="flex items-center gap-3 text-[#22c55e] font-bold text-xs uppercase tracking-widest">
            <ShieldCheck className="w-4 h-4" /> Section 03
          </div>
          <h2 className="text-2xl md:text-3xl font-extrabold text-white">
            Our Philosophy: Trust Comes First
          </h2>
          <p className="text-[#a1a1aa] leading-relaxed text-base">
            We operate under a single non-negotiable rule: <strong className="text-white">Commercial monetization never influences our AI recommendations, search rankings, or comparison scores.</strong>
          </p>
          <ul className="space-y-3 text-xs text-[#a1a1aa]">
            <li className="flex items-start gap-2">
              <span className="text-[#22c55e] font-bold">✓</span>
              <span><strong>Objective Recommendations:</strong> AI algorithms evaluate specs, price history, and 5-year TCO unbiased by commissions.</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-[#22c55e] font-bold">✓</span>
              <span><strong>Isolated Affiliate Engine:</strong> Affiliate links are attached strictly AFTER recommendation scoring is complete.</span>
            </li>
          </ul>
        </motion.section>

        {/* Section 4: How AI Helps */}
        <motion.section
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="space-y-6 border-t border-theme-border/40 pt-16"
        >
          <div className="flex items-center gap-3 text-[#3b82f6] font-bold text-xs uppercase tracking-widest">
            <Zap className="w-4 h-4" /> Section 04
          </div>
          <h2 className="text-2xl md:text-3xl font-extrabold text-white">
            How AI Helps: Instant Clarity
          </h2>
          <p className="text-[#a1a1aa] leading-relaxed text-base">
            Brand Battle synthesizes 5 independent AI systems—Product Knowledge Graph, Hybrid Matching, Price Intelligence, Marketplace Trust, and Decision Intelligence—into a single 5-System Consensus Score.
          </p>
        </motion.section>

        {/* Section 5: The Future & CTA */}
        <motion.section
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center p-10 rounded-3xl bg-theme-elevated/60 border border-theme-border space-y-6"
        >
          <div className="inline-flex items-center gap-2 text-xs font-bold text-[#22c55e] uppercase tracking-widest">
            <Target className="w-4 h-4" /> Section 05 — The Future
          </div>
          <h2 className="text-3xl font-extrabold text-white">
            Experience Honest Shopping Today
          </h2>
          <p className="text-sm text-[#a1a1aa] max-w-xl mx-auto">
            Compare products side-by-side, verify historical prices, and let transparent AI guide your next purchase decision.
          </p>
          <div className="pt-4 flex justify-center gap-4">
            <Link
              href="/compare"
              className="inline-flex items-center gap-2 px-6 py-3 rounded-full bg-[#f20ab0] text-white font-semibold text-sm hover:bg-[#d00898] transition shadow-lg shadow-[#f20ab030]"
            >
              Start Product Comparison <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </motion.section>
      </main>
    </div>
  )
}

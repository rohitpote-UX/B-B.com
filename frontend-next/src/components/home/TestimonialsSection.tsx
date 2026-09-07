'use client'

import React from 'react'
import { motion } from 'framer-motion'
import { ShieldCheck, Terminal, Award, ArrowUpRight, Mail } from 'lucide-react'

interface PillarItem {
  type: 'person' | 'system' | 'standard'
  name: string
  role: string
  organization: string
  initials: string
  tag: string
  description: string
  links?: {
    email?: string
    xHandle?: string
    xUrl?: string
  }
}

const PILLARS: PillarItem[] = [
  {
    type: 'person',
    name: 'Rohit Pote',
    role: 'Founder & Principal Architect',
    organization: 'Goldspade',
    initials: 'RP',
    tag: 'LEADERSHIP & ARCHITECTURE',
    description:
      'Directs the core product architecture, autonomous marketplace scrapers, anomaly quarantine models, and multi-source consensus scoring engines behind BrandBattle.',
    links: {
      email: 'crohitpote17@gmail.com',
      xHandle: '@GoldspadeFF',
      xUrl: 'https://x.com/GoldspadeFF',
    },
  },
  {
    type: 'system',
    name: 'Goldspade Data Infrastructure',
    role: 'Autonomous Ingestion & Verification',
    organization: 'Goldspade Core Systems',
    initials: 'GS',
    tag: 'DATA PIPELINES',
    description:
      'Distributed worker clusters continuously tracking prices, offer availability, and historical discount baselines across Amazon, Flipkart, Croma, and Reliance Digital with multi-tier TTL freshness.',
  },
  {
    type: 'standard',
    name: 'BrandBattle Trust Protocol',
    role: 'Algorithmic Neutrality & Governance',
    organization: 'Platform Integrity Standards',
    initials: 'BB',
    tag: 'VERIFICATION STANDARDS',
    description:
      'Strict zero-pay-for-rank policy. Product comparison scores and deal authentication are computed purely through verified mathematical value and historical price data with zero sponsored bias.',
  },
]

export default function TestimonialsSection() {
  return (
    <section className="relative py-28 bg-[#07070b] text-white border-b border-white/10 overflow-hidden">
      {/* Background ambient lighting */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[400px] bg-[#ff1695]/5 blur-[160px] rounded-full pointer-events-none" />

      <div className="w-full max-w-[1536px] mx-auto px-6 sm:px-10 lg:px-16 relative z-10">
        
        {/* Factual Header */}
        <div className="text-center max-w-3xl mx-auto mb-20">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/[0.04] border border-white/10 mb-4">
            <ShieldCheck className="w-3.5 h-3.5 text-[#ff1695]" />
            <span className="text-xs font-mono tracking-widest uppercase text-white/70">
              CORE TEAM & ARCHITECTURE
            </span>
          </div>
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-[var(--font-display)] font-semibold tracking-tight uppercase">
            Built By <span className="text-[#ff1695] italic">Engineers & Architects.</span>
          </h2>
          <p className="mt-4 text-sm sm:text-base text-white/60 font-light max-w-2xl mx-auto leading-relaxed">
            BrandBattle is engineered by Goldspade with an uncompromising commitment to algorithmic neutrality, mathematical price verification, and genuine consumer trust.
          </p>
        </div>

        {/* 3-Column Honest Team & Architecture Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {PILLARS.map((item, idx) => (
            <motion.div
              key={idx}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6, delay: idx * 0.12 }}
              className="group relative rounded-3xl bg-white/[0.02] hover:bg-white/[0.04] border border-white/10 hover:border-[#ff1695]/40 p-8 backdrop-blur-2xl transition-all duration-500 shadow-xl flex flex-col justify-between"
            >
              <div>
                {/* Top Badge & Indicator */}
                <div className="flex justify-between items-center mb-6">
                  <span className="text-[0.65rem] font-mono uppercase tracking-widest px-2.5 py-1 rounded-full bg-white/5 border border-white/10 text-white/70">
                    {item.tag}
                  </span>
                  {item.type === 'person' && (
                    <span className="text-xs font-mono text-[#ff1695]">Verified Leader</span>
                  )}
                  {item.type === 'system' && (
                    <Terminal className="w-4 h-4 text-white/30 group-hover:text-[#ff1695] transition-colors" />
                  )}
                  {item.type === 'standard' && (
                    <Award className="w-4 h-4 text-white/30 group-hover:text-[#ff1695] transition-colors" />
                  )}
                </div>

                {/* Factual Description (Zero Fake Quotes) */}
                <p className="text-sm sm:text-base text-white/80 font-light leading-relaxed mb-8">
                  {item.description}
                </p>
              </div>

              {/* Author / Entity Info with Tasteful Initials Avatar */}
              <div className="pt-6 border-t border-white/10">
                <div className="flex items-center gap-4 mb-4">
                  <div
                    className={`w-12 h-12 rounded-full overflow-hidden border flex items-center justify-center font-mono font-bold text-sm shrink-0 transition-all duration-500 ${
                      item.type === 'person'
                        ? 'bg-gradient-to-br from-[#ff1695]/20 to-white/5 border-[#ff1695]/50 text-white group-hover:border-[#ff1695]'
                        : 'bg-white/5 border-white/20 text-white/80 group-hover:border-white/40'
                    }`}
                    aria-label={`${item.name} initials`}
                  >
                    <span>{item.initials}</span>
                  </div>
                  <div>
                    <h3 className="text-sm font-bold text-white group-hover:text-[#ff1695] transition-colors">
                      {item.name}
                    </h3>
                    <p className="text-xs font-mono text-white/50">{item.role}</p>
                    <p className="text-[0.7rem] text-white/40 mt-0.5">{item.organization}</p>
                  </div>
                </div>

                {/* Direct Verified Links (if available) */}
                {item.links && (
                  <div className="flex items-center gap-4 pt-3 border-t border-white/5 text-xs">
                    {item.links.xUrl && (
                      <a
                        href={item.links.xUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-1 text-white/60 hover:text-white transition-colors"
                        aria-label={`Follow ${item.name} on X ${item.links.xHandle}`}
                      >
                        <span>{item.links.xHandle}</span>
                        <ArrowUpRight className="w-3 h-3 opacity-60" />
                      </a>
                    )}
                    {item.links.email && (
                      <a
                        href={`mailto:${item.links.email}`}
                        className="inline-flex items-center gap-1 text-white/60 hover:text-[#ff1695] transition-colors ml-auto"
                        aria-label={`Email ${item.name} at ${item.links.email}`}
                      >
                        <Mail className="w-3 h-3" />
                        <span>Direct</span>
                      </a>
                    )}
                  </div>
                )}
              </div>

              {/* Subtle Ambient Card Glow */}
              <div className="absolute inset-0 rounded-3xl bg-gradient-to-r from-[#ff1695]/0 via-[#ff1695]/10 to-[#ff1695]/0 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none" />
            </motion.div>
          ))}
        </div>

      </div>
    </section>
  )
}

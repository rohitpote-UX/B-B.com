'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import Link from 'next/link'
import { Cpu, Sparkles, ArrowRight, CheckCircle2, MessageSquareText, Shield, ThumbsUp } from 'lucide-react'

const SAMPLE_PROMPTS = [
  {
    text: 'Best ANC headphones under $350 for long-haul flights & daily office work',
    resultProduct: 'Sony WH-1000XM5',
    matchScore: 98,
    reason: 'Top active noise cancellation in class (-30dB cabin noise isolation), 30h battery life, lightweight 250g ergonomics.',
  },
  {
    text: 'Top workstation laptop for 4K video editing & 10+ hour battery',
    resultProduct: 'MacBook Pro 16" M3 Max',
    matchScore: 97,
    reason: 'Hardware media engines handle dual 8K ProRes streams with zero fan noise while maintaining 18h real battery.',
  },
  {
    text: 'Flagship camera phone under $1,200 with best low-light zoom',
    resultProduct: 'Samsung Galaxy S24 Ultra',
    matchScore: 95,
    reason: '50MP 5x optical telephoto with Quad Tele sensor system & Nightography processing outperforms competitors in low light.',
  },
]

export default function RecommendationChapter() {
  const [selectedPromptIndex, setSelectedPromptIndex] = useState(0)

  const activePrompt = SAMPLE_PROMPTS[selectedPromptIndex]

  return (
    <section className="relative py-20 sm:py-28 bg-[#050505] text-white overflow-hidden border-b border-white/10">
      {/* Ambient background glow */}
      <div className="absolute top-1/4 right-10 w-[600px] h-[600px] bg-[#ff1695]/10 blur-[160px] rounded-full pointer-events-none" />

      <div className="w-full max-w-[1536px] mx-auto px-4 sm:px-10 lg:px-16 relative z-10">
        
        {/* Chapter Header */}
        <div className="grid grid-cols-12 gap-6 sm:gap-8 mb-12 sm:mb-16 items-end">
          <div className="col-span-12 lg:col-span-7">
            <div className="flex items-center gap-2 mb-3">
              <span className="text-[#ff1695] font-mono text-xs tracking-widest font-semibold uppercase">
                CHAPTER 04
              </span>
              <span className="text-white/30 text-xs">/</span>
              <span className="text-white/60 font-mono text-xs tracking-widest uppercase">
                AI RECOMMENDATION GRAPH
              </span>
            </div>
            <h2 className="text-3xl sm:text-4xl md:text-5xl font-[var(--font-display)] font-semibold tracking-tight uppercase leading-tight">
              Personalized Matching. <span className="text-[#ff1695] italic">Zero Affiliate Bias.</span>
            </h2>
          </div>
          <div className="col-span-12 lg:col-span-5">
            <p className="text-white/60 text-sm sm:text-base font-light leading-relaxed">
              Generic buyer guides push sponsored products with high commission rates. Brand Battle uses an autonomous neural graph that ranks products solely by engineering merit.
            </p>
          </div>
        </div>

        {/* Interactive AI Advisor Demo Card */}
        <div className="rounded-3xl bg-gradient-to-b from-white/[0.04] to-white/[0.01] border border-white/15 p-4 sm:p-6 lg:p-10 backdrop-blur-2xl shadow-2xl relative max-w-full overflow-hidden">
          
          <div className="grid grid-cols-12 gap-6 sm:gap-8 items-center">
            
            {/* LEFT: PROMPT TRIGGER LIST */}
            <div className="col-span-12 lg:col-span-6 space-y-3 sm:space-y-4">
              <div className="flex items-center gap-2 mb-2">
                <Sparkles className="w-4 h-4 text-[#ff1695]" />
                <span className="text-[0.65rem] sm:text-xs font-mono tracking-widest uppercase text-white/80">
                  SAMPLE AI PROMPT QUERIES
                </span>
              </div>

              {SAMPLE_PROMPTS.map((prompt, idx) => {
                const isActive = idx === selectedPromptIndex
                return (
                  <button
                    key={idx}
                    onClick={() => setSelectedPromptIndex(idx)}
                    className={`w-full text-left p-3.5 sm:p-4 rounded-2xl border transition-all duration-300 max-w-full overflow-hidden ${
                      isActive
                        ? 'bg-[#ff1695]/10 border-[#ff1695]/50 text-white shadow-[0_0_25px_rgba(255,22,149,0.2)]'
                        : 'bg-white/[0.02] border-white/[0.08] text-white/70 hover:text-white hover:bg-white/[0.05]'
                    }`}
                  >
                    <div className="flex items-start gap-2.5 sm:gap-3 max-w-full">
                      <MessageSquareText className={`w-4 h-4 mt-0.5 shrink-0 ${isActive ? 'text-[#ff1695]' : 'text-white/40'}`} />
                      <div className="flex-1 min-w-0">
                        <p className="text-xs sm:text-sm font-medium leading-snug break-words whitespace-normal">
                          &quot;{prompt.text}&quot;
                        </p>
                        {/* Responsive Vertical Stack under 768px for Target Match & Score */}
                        <div className="flex flex-col sm:flex-row sm:items-center gap-1 sm:gap-3 mt-2 text-[0.65rem] sm:text-[0.7rem] font-mono text-white/40 max-w-full">
                          <span className="break-words whitespace-normal leading-tight">
                            Target Match: <span className="text-white/80 font-medium">{prompt.resultProduct}</span>
                          </span>
                          <span className="hidden sm:inline">•</span>
                          <span className="text-[#ff1695] font-semibold">Score: {prompt.matchScore}%</span>
                        </div>
                      </div>
                    </div>
                  </button>
                )
              })}

              <div className="pt-2">
                <Link
                  href="/advisor"
                  className="inline-flex items-center gap-2 text-xs font-mono uppercase tracking-wider text-[#ff1695] hover:text-[#e00d7f] font-bold transition-colors group min-h-[48px]"
                >
                  <span>Launch Interactive AI Advisor</span>
                  <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-1" />
                </Link>
              </div>
            </div>

            {/* RIGHT: AI MATCHING GRAPH RESULT PREVIEW */}
            <div className="col-span-12 lg:col-span-6">
              <motion.div
                key={selectedPromptIndex}
                initial={{ opacity: 0, scale: 0.96 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.4 }}
                className="rounded-2xl bg-black/60 border border-white/15 p-4 sm:p-6 space-y-4 sm:space-y-6 backdrop-blur-xl relative max-w-full overflow-hidden"
              >
                {/* Result Top Bar */}
                <div className="flex items-center justify-between pb-4 border-b border-white/10 gap-2">
                  <div className="flex items-center gap-2">
                    <Cpu className="w-4 h-4 text-[#ff1695] shrink-0" />
                    <span className="text-[0.65rem] sm:text-xs font-mono text-white/80">NEURAL ENGINE OUTPUT</span>
                  </div>
                  <span className="px-2.5 py-1 rounded-full bg-emerald-500/20 text-emerald-400 text-[0.65rem] sm:text-xs font-mono font-bold shrink-0">
                    {activePrompt.matchScore}% CONFIDENCE
                  </span>
                </div>

                {/* Match Result Details */}
                <div>
                  <span className="text-[0.65rem] sm:text-[0.7rem] font-mono text-white/50 uppercase tracking-wider">
                    RECOMMENDED HARDWARE MATCH
                  </span>
                  <h3 className="text-lg sm:text-xl font-bold text-white mt-1 break-words">
                    {activePrompt.resultProduct}
                  </h3>

                  <div className="mt-4 p-3.5 sm:p-4 rounded-xl bg-white/[0.03] border border-white/10 space-y-2">
                    <div className="flex items-center gap-2 text-xs font-mono text-[#ff1695] font-bold">
                      <Shield className="w-3.5 h-3.5 shrink-0" />
                      <span>EXPLAINABLE AI RATIONALE</span>
                    </div>
                    <p className="text-xs text-white/80 font-light leading-relaxed break-words whitespace-normal">
                      {activePrompt.reason}
                    </p>
                  </div>
                </div>

                {/* Micro Metrics */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 sm:gap-3 pt-2 border-t border-white/10 text-xs font-mono">
                  <div className="flex items-center gap-2 text-white/70">
                    <CheckCircle2 className="w-4 h-4 text-[#ff1695] shrink-0" />
                    <span>0% Affiliate Bias</span>
                  </div>
                  <div className="flex items-center gap-2 text-white/70">
                    <ThumbsUp className="w-4 h-4 text-[#ff1695] shrink-0" />
                    <span>100% User Workflow Aligned</span>
                  </div>
                </div>
              </motion.div>
            </div>

          </div>

        </div>

      </div>
    </section>
  )
}

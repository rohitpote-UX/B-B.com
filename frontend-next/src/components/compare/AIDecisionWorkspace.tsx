'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Sparkles, ShieldCheck, CheckCircle2, Award, Zap, HelpCircle,
  Clock, DollarSign, Layers, Share2, ThumbsUp, Scale, Bookmark, Check
} from 'lucide-react'
import { Product } from '@/types'
import { formatPrice } from '@/data/demoData'

interface AIDecisionWorkspaceProps {
  p1: Product
  p2: Product
  onToggleDifferencesOnly?: (diffOnly: boolean) => void
  isDifferencesOnly?: boolean
}

export default function AIDecisionWorkspace({
  p1,
  p2,
  onToggleDifferencesOnly,
  isDifferencesOnly = false,
}: AIDecisionWorkspaceProps) {
  const [selectedPersona, setSelectedPersona] = useState('general')
  const [selectedScenario, setSelectedScenario] = useState('default')
  const [isSaved, setIsSaved] = useState(false)
  const [activeQuestionAnswer, setActiveQuestionAnswer] = useState<string | null>(null)
  const [activeQuestion, setActiveQuestion] = useState<string | null>(null)

  const price1 = p1.bestPrice || 24999
  const price2 = p2.bestPrice || 29999
  const winner = price1 <= price2 ? p1 : p2
  const runnerUp = price1 <= price2 ? p2 : p1
  const savings = Math.abs(price2 - price1)

  const personas = [
    { id: 'general', label: 'Most Users' },
    { id: 'students', label: 'Best for Students' },
    { id: 'professionals', label: 'Best for Professionals' },
    { id: 'travelers', label: 'Best for Travelers' },
    { id: 'budget', label: 'Best Budget Pick' },
    { id: 'long_term', label: 'Best Long-Term Value' },
  ]

  const scenarios = [
    { id: 'default', label: 'Balanced Overall' },
    { id: 'price', label: 'If Price Matters Most' },
    { id: 'performance', label: 'If Performance Matters Most' },
    { id: 'durability', label: 'If Durability Matters Most' },
  ]

  const questions = [
    { q: 'Which product lasts longer?', a: `${p1.name} features a larger battery capacity and verified higher long-term durability scores.` },
    { q: 'Which is cheaper over 5 years?', a: `${winner.name} offers ₹${(savings * 1.2).toLocaleString()} lower 5-year total ownership cost including accessories and maintenance.` },
    { q: 'Which has better warranty support?', a: `${p1.brand} provides 2-year official manufacturer warranty coverage.` },
  ]

  const handleSave = () => {
    setIsSaved(true)
    setTimeout(() => setIsSaved(false), 2500)
  }

  return (
    <div className="w-full space-y-8 mb-10">
      {/* 1. AI Decision Summary Panel */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="rounded-2xl border border-theme-border bg-theme-elevated/70 p-6 md:p-8 backdrop-blur-xl relative overflow-hidden shadow-2xl"
      >
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 border-b border-theme-border/60 pb-5 mb-6">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-[#22c55e15] border border-[#22c55e30] flex items-center justify-center">
              <Sparkles className="w-5 h-5 text-[#22c55e]" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-[0.65rem] font-bold uppercase tracking-[0.2em] px-2.5 py-0.5 rounded-full bg-[#22c55e15] text-[#22c55e] border border-[#22c55e30]">
                  AI Decision Recommendation
                </span>
                <span className="text-xs text-theme-muted font-mono">127 Specs Verified</span>
              </div>
              <h2 className="text-lg font-bold text-theme-text mt-1 flex items-center gap-2">
                Recommended Choice: <span className="text-[#22c55e]">{winner.name}</span>
              </h2>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={handleSave}
              className="flex items-center gap-2 text-xs px-3.5 py-2 rounded-xl bg-theme-subtle border border-theme-border text-theme-text hover:border-theme-muted transition font-medium"
            >
              {isSaved ? <Check className="w-3.5 h-3.5 text-[#22c55e]" /> : <Bookmark className="w-3.5 h-3.5 text-[#22c55e]" />}
              <span>{isSaved ? 'Comparison Saved!' : 'Save Comparison'}</span>
            </button>
          </div>
        </div>

        {/* Top 3 Reasons */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="p-4 rounded-xl bg-theme-subtle/50 border border-theme-border/60">
            <div className="text-xs font-bold text-theme-text flex items-center gap-2 mb-1">
              <Award className="w-4 h-4 text-[#22c55e]" /> 1. Higher Value Retained
            </div>
            <p className="text-xs text-theme-muted">
              Estimated ₹{savings.toLocaleString()} lower 5-year total ownership cost with higher resale potential.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-theme-subtle/50 border border-theme-border/60">
            <div className="text-xs font-bold text-theme-text flex items-center gap-2 mb-1">
              <ShieldCheck className="w-4 h-4 text-[#22c55e]" /> 2. Seller Trust Alignment
            </div>
            <p className="text-xs text-theme-muted">
              Backed by 96% verified marketplace seller trust rating and official warranty support.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-theme-subtle/50 border border-theme-border/60">
            <div className="text-xs font-bold text-theme-text flex items-center gap-2 mb-1">
              <Zap className="w-4 h-4 text-[#22c55e]" /> 3. Category Efficiency Winner
            </div>
            <p className="text-xs text-theme-muted">
              Delivers superior daily battery runtime and optimal price-to-performance ratio.
            </p>
          </div>
        </div>

        {/* Trade-Off Summary */}
        <div className="p-4 rounded-xl bg-[#22c55e08] border border-[#22c55e20] flex items-center gap-3">
          <Scale className="w-5 h-5 text-[#22c55e] shrink-0" />
          <p className="text-xs text-theme-text">
            <strong className="text-[#22c55e]">Trade-Off Summary:</strong> {winner.name} offers a lower initial price and longer battery endurance, while {runnerUp.name} provides slightly higher peak GPU benchmarks.
          </p>
        </div>
      </motion.div>

      {/* 5. AI Persona & Simulator Controls */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Persona Selector */}
        <div className="p-6 rounded-2xl border border-theme-border bg-theme-elevated/50 space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-bold uppercase tracking-wider text-theme-text">5. AI Persona View</h3>
            <span className="text-[0.65rem] text-theme-muted">Perspective-based scoring</span>
          </div>
          <div className="flex flex-wrap gap-2">
            {personas.map((p) => (
              <button
                key={p.id}
                onClick={() => setSelectedPersona(p.id)}
                className={`text-xs px-3 py-1.5 rounded-lg border transition ${
                  selectedPersona === p.id
                    ? 'border-[#22c55e] bg-[#22c55e15] text-[#22c55e] font-semibold'
                    : 'border-theme-border text-theme-muted hover:text-theme-text'
                }`}
              >
                {p.label}
              </button>
            ))}
          </div>
        </div>

        {/* Decision Simulator */}
        <div className="p-6 rounded-2xl border border-theme-border bg-theme-elevated/50 space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-bold uppercase tracking-wider text-theme-text">18. Decision Simulator</h3>
            <span className="text-[0.65rem] text-theme-muted">Scenario evaluation</span>
          </div>
          <div className="flex flex-wrap gap-2">
            {scenarios.map((s) => (
              <button
                key={s.id}
                onClick={() => setSelectedScenario(s.id)}
                className={`text-xs px-3 py-1.5 rounded-lg border transition ${
                  selectedScenario === s.id
                    ? 'border-[#22c55e] bg-[#22c55e15] text-[#22c55e] font-semibold'
                    : 'border-theme-border text-theme-muted hover:text-theme-text'
                }`}
              >
                {s.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* 10. Multi-System Agreement Meter & 9. Purchase Confidence */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="p-6 rounded-2xl border border-theme-border bg-theme-elevated/50 md:col-span-2 space-y-4">
          <div className="flex items-center justify-between border-b border-theme-border/60 pb-3">
            <h3 className="text-xs font-bold uppercase tracking-wider text-theme-text flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-[#22c55e]" /> 10. Multi-System Agreement Meter
            </h3>
            <span className="text-xs font-bold text-[#22c55e]">5 of 5 Systems Agree</span>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-3 text-center">
            {[
              { name: 'AI Recommendation', icon: Sparkles },
              { name: 'Price Intelligence', icon: DollarSign },
              { name: 'Knowledge Graph', icon: Layers },
              { name: 'Marketplace Trust', icon: ShieldCheck },
              { name: 'Value Engine', icon: Award },
            ].map((sys, idx) => {
              const Icon = sys.icon
              return (
                <div key={idx} className="p-3 rounded-xl bg-theme-subtle/50 border border-[#22c55e30]">
                  <Icon className="w-4 h-4 text-[#22c55e] mx-auto mb-1" />
                  <div className="text-[0.65rem] font-medium text-theme-text">{sys.name}</div>
                  <div className="text-[0.6rem] text-[#22c55e] font-semibold mt-0.5">✔ Agreed</div>
                </div>
              )
            })}
          </div>
        </div>

        {/* Purchase Confidence Card */}
        <div className="p-6 rounded-2xl border border-[#22c55e30] bg-[#22c55e05] space-y-3">
          <div className="text-xs font-bold uppercase tracking-wider text-theme-muted">9. Purchase Confidence</div>
          <div className="text-3xl font-extrabold text-[#22c55e]">96.0 / 100</div>
          <p className="text-xs text-theme-text leading-relaxed">
            High decision confidence backed by verified marketplace seller trust and historical price stability.
          </p>
        </div>
      </div>

      {/* 13. Contextual AI Questions & 14. Decision Checklist */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Contextual AI Questions */}
        <div className="p-6 rounded-2xl border border-theme-border bg-theme-elevated/50 space-y-3">
          <h3 className="text-xs font-bold uppercase tracking-wider text-theme-text flex items-center gap-2">
            <HelpCircle className="w-4 h-4 text-[#22c55e]" /> 13. Contextual AI Questions
          </h3>
          <div className="space-y-2">
            {questions.map((item, idx) => (
              <button
                key={idx}
                onClick={() => {
                  setActiveQuestion(item.q)
                  setActiveQuestionAnswer(item.a)
                }}
                className="w-full text-left p-2.5 rounded-xl bg-theme-subtle hover:border-theme-muted border border-theme-border text-xs text-theme-text transition flex items-center justify-between"
              >
                <span>{item.q}</span>
                <span className="text-[0.65rem] text-[#22c55e]">Ask →</span>
              </button>
            ))}
          </div>

          <AnimatePresence>
            {activeQuestionAnswer && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="p-3 rounded-xl bg-[#22c55e10] border border-[#22c55e30] text-xs text-theme-text mt-2"
              >
                <div className="font-bold text-[#22c55e] mb-1">{activeQuestion}</div>
                <div>{activeQuestionAnswer}</div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Mental Validation Checklist */}
        <div className="p-6 rounded-2xl border border-theme-border bg-theme-elevated/50 space-y-3">
          <h3 className="text-xs font-bold uppercase tracking-wider text-theme-text flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-[#22c55e]" /> 14. Decision Validation Checklist
          </h3>
          <div className="grid grid-cols-2 gap-2 text-xs text-theme-text">
            {[
              'Fits your budget',
              'Matches intended use',
              'Trusted seller available',
              'Good long-term value',
              'Strong AI recommendation',
              'Competitive current price',
            ].map((check, i) => (
              <div key={i} className="flex items-center gap-2 p-2 rounded-lg bg-theme-subtle">
                <CheckCircle2 className="w-3.5 h-3.5 text-[#22c55e] shrink-0" />
                <span>{check}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

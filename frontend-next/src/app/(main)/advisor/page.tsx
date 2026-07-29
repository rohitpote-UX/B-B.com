'use client'

import { useState, useRef, useEffect, useMemo } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Brain, Trash2, Sparkles, ChevronRight, Send, Search, User
} from 'lucide-react'
import { processQuery, loadMemory, saveMemory, QUICK_CHIPS } from '@/data/aiEngine'
import AIResponseCard from '@/components/ai/AIResponseCard'
import { AIMessage } from '@/types'

// ── Typing animation steps ──
const TYPING_STEPS = [
  'Understanding your needs...',
  'Searching 1,400+ products...',
  'Ranking with AI scoring...',
  'Building recommendation...',
]

export default function AIAdvisorPage() {
  const [messages, setMessages] = useState<AIMessage[]>([])
  const [input, setInput] = useState('')
  const [typing, setTyping] = useState(false)
  const [typingStep, setTypingStep] = useState(0)
  const [memory, setMemory] = useState(() => loadMemory())
  const [showMemory, setShowMemory] = useState(false)
  const scrollContainerRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  // Auto-scroll on new messages
  useEffect(() => {
    if (scrollContainerRef.current) {
      setTimeout(() => {
        scrollContainerRef.current?.scrollTo({
          top: scrollContainerRef.current.scrollHeight,
          behavior: 'smooth'
        })
      }, 100)
    }
  }, [messages, typing])

  // Welcome message based on memory
  const welcomeMessage = useMemo(() => {
    if (memory.queryCount > 0 && memory.lastCategory) {
      return `Welcome back! I remember you were looking at ${memory.lastCategory}. Want me to find something similar, or exploring something new today?`
    }
    if (memory.preferredBrands?.length > 0) {
      return `Hey! I know you like ${memory.preferredBrands.map((b: string) => b.charAt(0).toUpperCase() + b.slice(1)).join(', ')}. Want me to find the best deals from those brands?`
    }
    return "Hey! I'm your AI shopping advisor. Tell me what you're looking for, and I'll find the perfect match from 1,400+ products across all major platforms."
  }, [memory])

  // Typing animation stepper
  useEffect(() => {
    if (!typing) return
    setTypingStep(0)
    const timers = TYPING_STEPS.map((_, i) =>
      setTimeout(() => setTypingStep(i), i * 400)
    )
    return () => timers.forEach(clearTimeout)
  }, [typing])

  // Send query
  const send = async (text = input) => {
    const trimmed = text.trim()
    if (!trimmed) return

    // Add user message
    setMessages(prev => [...prev, { role: 'user', content: trimmed }])
    setInput('')
    setTyping(true)

    // Simulate AI processing time
    await new Promise(r => setTimeout(r, 1200 + Math.random() * 600))

    // Run AI pipeline
    const { response, memory: updatedMemory } = processQuery(trimmed) as any

    // Add AI response
    setMessages(prev => [...prev, { role: 'assistant', data: response }])
    setMemory(updatedMemory)
    setTyping(false)

    // Focus input for next query
    inputRef.current?.focus()
  }

  const clearChat = () => {
    setMessages([])
  }

  const clearMemory = () => {
    const blank = { preferredBrands: [], budgetRange: null, useCases: [], categoriesExplored: [], queryCount: 0, lastCategory: null }
    saveMemory(blank)
    setMemory(blank)
  }

  const hasConversation = messages.length > 0

  return (
    <div className="min-h-screen pt-32 pb-20 flex flex-col items-center px-4">

      {/* ══════ HEADER ══════ */}
      <div className="w-full max-w-4xl mb-6">
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center gap-2 mb-3">
              <span className="text-[0.65rem] font-bold uppercase tracking-[0.2em] text-theme-muted">Intelligence Engine</span>
              <span className="px-2 py-0.5 rounded-full bg-[#22c55e15] border border-[#22c55e25] text-[0.5rem] font-bold text-[#22c55e] uppercase tracking-widest">v3.0</span>
            </div>
            <h1 className="text-[2rem] sm:text-[3rem] font-[var(--font-display)] font-medium leading-[1.1] tracking-tight text-theme-text">AI Advisor.</h1>
          </div>

          {/* Memory indicator */}
          <button onClick={() => setShowMemory(!showMemory)} className="flex items-center gap-2 px-3 py-2 rounded-xl border border-theme-border bg-theme-elevated hover:border-theme-strong transition-all">
            <Brain className="w-4 h-4 text-[#a855f7]" />
            <span className="text-[0.6rem] font-bold uppercase tracking-widest text-theme-muted hidden sm:block">Memory</span>
            {memory.queryCount > 0 && (
              <span className="w-4 h-4 rounded-full bg-[#a855f7] text-white text-[0.5rem] font-bold flex items-center justify-center">{memory.queryCount}</span>
            )}
          </button>
        </div>

        <p className="text-[0.9rem] text-theme-secondary max-w-xl mt-3 leading-relaxed">
          Your AI-powered buying intelligence. Ask anything about products — I analyze real data, not guesses.
        </p>
      </div>

      {/* ══════ MEMORY PANEL ══════ */}
      <AnimatePresence>
        {showMemory && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="w-full max-w-4xl overflow-hidden mb-4"
          >
            <div className="bg-theme-elevated border border-[#a855f720] rounded-2xl p-5">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                  <Brain className="w-4 h-4 text-[#a855f7]" />
                  <span className="text-[0.65rem] font-bold uppercase tracking-[0.15em] text-[#a855f7]">AI Memory</span>
                </div>
                <button onClick={clearMemory} className="flex items-center gap-1 text-[0.6rem] text-theme-dim hover:text-[#ef4444] transition-colors uppercase tracking-widest">
                  <Trash2 className="w-3 h-3" /> Clear
                </button>
              </div>

              {memory.queryCount === 0 ? (
                <p className="text-[0.75rem] text-theme-dim italic">No memory yet. Start chatting and I'll learn your preferences!</p>
              ) : (
                <div className="space-y-3">
                  {memory.preferredBrands.length > 0 && (
                    <div>
                      <p className="text-[0.6rem] text-theme-dim uppercase tracking-widest mb-1.5">Favorite Brands</p>
                      <div className="flex flex-wrap gap-1.5">
                        {memory.preferredBrands.map((b: string, i: number) => (
                          <span key={i} className="px-2.5 py-1 rounded-full bg-[#3b82f612] border border-[#3b82f625] text-[0.6rem] font-medium text-[#3b82f6] capitalize">{b}</span>
                        ))}
                      </div>
                    </div>
                  )}
                  {memory.useCases.length > 0 && (
                    <div>
                      <p className="text-[0.6rem] text-theme-dim uppercase tracking-widest mb-1.5">Interests</p>
                      <div className="flex flex-wrap gap-1.5">
                        {memory.useCases.map((uc: string, i: number) => (
                          <span key={i} className="px-2.5 py-1 rounded-full bg-[#22c55e12] border border-[#22c55e25] text-[0.6rem] font-medium text-[#22c55e] capitalize">{uc}</span>
                        ))}
                      </div>
                    </div>
                  )}
                  {memory.categoriesExplored.length > 0 && (
                    <div>
                      <p className="text-[0.6rem] text-theme-dim uppercase tracking-widest mb-1.5">Categories Explored</p>
                      <div className="flex flex-wrap gap-1.5">
                        {memory.categoriesExplored.map((cat: string, i: number) => (
                          <span key={i} className="px-2.5 py-1 rounded-full bg-[#f59e0b12] border border-[#f59e0b25] text-[0.6rem] font-medium text-[#f59e0b]">{cat}</span>
                        ))}
                      </div>
                    </div>
                  )}
                  {memory.budgetRange && (
                    <p className="text-[0.7rem] text-theme-secondary">Budget preference: <span className="font-medium text-theme-text">under ${memory.budgetRange}</span></p>
                  )}
                  <p className="text-[0.6rem] text-theme-dim">{memory.queryCount} queries processed</p>
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* ══════ CHAT CONTAINER ══════ */}
      <div className="w-full max-w-4xl flex flex-col flex-1 min-h-[65vh] border border-theme-border bg-theme-bg rounded-2xl overflow-hidden">

        {/* Chat Header */}
        <div className="border-b border-theme-border px-5 py-3 flex justify-between items-center bg-theme-elevated/50">
          <div className="flex items-center gap-3">
            <div className="relative">
              <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-[#22c55e20] to-[#3b82f620] flex items-center justify-center border border-[#22c55e20]">
                <Sparkles className="w-4 h-4 text-[#22c55e]" />
              </div>
              <span className="absolute -bottom-0.5 -right-0.5 w-2.5 h-2.5 rounded-full bg-[#22c55e] border-2 border-theme-elevated" />
            </div>
            <div>
              <span className="text-[0.7rem] font-bold text-theme-text block">BrandBattle AI</span>
              <span className="text-[0.55rem] text-[#22c55e] uppercase tracking-widest">Online · AI-Powered Buying Intelligence</span>
            </div>
          </div>
          {hasConversation && (
            <button onClick={clearChat} className="flex items-center gap-1 text-[0.6rem] text-theme-dim hover:text-theme-text transition-colors uppercase tracking-widest px-2 py-1 rounded-lg hover:bg-theme-subtle">
              <Trash2 className="w-3 h-3" /> Clear
            </button>
          )}
        </div>

        {/* Messages Area */}
        <div ref={scrollContainerRef} className="flex-1 overflow-y-auto p-5 lg:p-8 space-y-6 relative">

          {/* Welcome State */}
          {!hasConversation && !typing && (
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ type: 'spring', stiffness: 200, damping: 20 }}
                className="w-20 h-20 rounded-3xl bg-gradient-to-br from-[#22c55e15] to-[#a855f715] flex items-center justify-center border border-[#22c55e15] mb-6"
              >
                <Sparkles className="w-10 h-10 text-[#22c55e]" />
              </motion.div>

              <h2 className="text-[1.5rem] font-[var(--font-display)] font-medium text-theme-text mb-3">What are you shopping for?</h2>
              <p className="text-[0.85rem] text-theme-secondary max-w-md mb-8 leading-relaxed">{welcomeMessage}</p>

              {/* Quick Chip Grid */}
              <div className="flex flex-wrap gap-2 justify-center max-w-lg">
                {QUICK_CHIPS.map((chip: { label: string; query: string }, i: number) => (
                  <motion.button
                    key={i}
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 0.1 + i * 0.04 }}
                    onClick={() => send(chip.query)}
                    className="group flex items-center gap-1.5 px-4 py-2 rounded-xl border border-theme-border bg-theme-elevated hover:border-[#22c55e40] hover:bg-[#22c55e05] transition-all duration-300 text-[0.7rem] font-medium text-theme-muted hover:text-[#22c55e]"
                  >
                    <span>{chip.label}</span>
                  </motion.button>
                ))}
              </div>

              {/* Suggestion examples */}
              <div className="mt-8 text-[0.7rem] text-theme-dim max-w-md">
                <p className="mb-2 text-[0.6rem] uppercase tracking-widest">Try asking:</p>
                <div className="space-y-1.5">
                  {['"Best laptop for students under $600"', '"Gaming phone with great battery"', '"Compare Sony vs Bose headphones"', '"Budget 4K TV for streaming"'].map((q, i) => (
                    <button key={i} onClick={() => send(q.replace(/"/g, ''))} className="block w-full text-left px-3 py-2 rounded-lg hover:bg-theme-elevated transition-colors text-theme-secondary hover:text-theme-text">
                      <ChevronRight className="w-3 h-3 inline mr-1.5 text-theme-dim" />{q}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Conversation Messages */}
          <AnimatePresence>
            {messages.map((msg, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
                className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                {/* Bot Avatar */}
                {msg.role === 'assistant' && (
                  <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-[#22c55e20] to-[#3b82f620] border border-[#22c55e20] flex items-center justify-center shrink-0 mt-1">
                    <Sparkles className="w-4 h-4 text-[#22c55e]" />
                  </div>
                )}

                <div className={`max-w-[90%] min-w-[200px] ${msg.role === 'user' ? 'order-1' : ''}`}>
                  {msg.role === 'user' ? (
                    /* User message bubble */
                    <div className="bg-theme-text text-theme-bg px-5 py-3 rounded-2xl rounded-br-sm">
                      <p className="text-[0.85rem] leading-relaxed">{msg.content}</p>
                    </div>
                  ) : (
                    /* AI structured response */
                    <AIResponseCard data={msg.data!} />
                  )}
                </div>

                {/* User Avatar */}
                {msg.role === 'user' && (
                  <div className="w-8 h-8 rounded-xl bg-theme-text flex items-center justify-center shrink-0 mt-1 order-2">
                    <User className="w-4 h-4 text-theme-bg" />
                  </div>
                )}
              </motion.div>
            ))}

            {/* Typing Indicator */}
            {typing && (
              <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="flex gap-3 items-start">
                <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-[#22c55e20] to-[#3b82f620] border border-[#22c55e20] flex items-center justify-center shrink-0">
                  <Sparkles className="w-4 h-4 text-[#22c55e]" />
                </div>
                <div className="bg-theme-elevated border border-theme-border rounded-2xl px-5 py-4">
                  <div className="flex items-center gap-3">
                    <div className="flex gap-1">
                      {[0, 1, 2].map(j => (
                        <motion.span
                          key={j}
                          className="w-2 h-2 rounded-full bg-[#22c55e]"
                          animate={{ opacity: [0.3, 1, 0.3] }}
                          transition={{ duration: 1, repeat: Infinity, delay: j * 0.2 }}
                        />
                      ))}
                    </div>
                    <AnimatePresence mode="wait">
                      <motion.span
                        key={typingStep}
                        initial={{ opacity: 0, y: 5 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -5 }}
                        className="text-[0.7rem] text-theme-muted"
                      >
                        {TYPING_STEPS[typingStep]}
                      </motion.span>
                    </AnimatePresence>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* ══════ INPUT BAR ══════ */}
        <div className="border-t border-theme-border p-4 lg:px-8 bg-theme-bg/80 backdrop-blur-sm">
          {/* Quick chips below chat (only after first message) */}
          {hasConversation && (
            <div className="flex gap-1.5 overflow-x-auto mb-3 pb-1 hide-scrollbar -mx-1 px-1">
              {QUICK_CHIPS.slice(0, 8).map((chip: { label: string; query: string }, i: number) => (
                <button
                  key={i}
                  onClick={() => send(chip.query)}
                  className="shrink-0 px-3 py-1.5 rounded-lg border border-theme-border text-[0.6rem] font-medium text-theme-muted hover:text-[#22c55e] hover:border-[#22c55e30] transition-all bg-theme-elevated"
                >
                  {chip.label}
                </button>
              ))}
            </div>
          )}

          <form onSubmit={e => { e.preventDefault(); send() }} className="flex items-center gap-3">
            <div className="flex-1 flex items-center gap-3 bg-theme-elevated border border-theme-border rounded-xl px-4 py-3 focus-within:border-[#22c55e40] focus-within:shadow-[0_0_20px_rgba(34,197,94,0.05)] transition-all">
              <Search className="w-4 h-4 text-theme-dim shrink-0" />
              <input
                ref={inputRef}
                type="text"
                value={input}
                onChange={e => setInput(e.target.value)}
                placeholder="Ask about any product, deal, or comparison..."
                className="flex-1 bg-transparent text-theme-text placeholder:text-theme-dim text-[0.85rem] focus:outline-none"
                disabled={typing}
              />
            </div>
            <motion.button
              type="submit"
              disabled={!input.trim() || typing}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="w-11 h-11 rounded-xl flex items-center justify-center transition-all disabled:opacity-20 disabled:cursor-not-allowed bg-[#22c55e] hover:bg-[#16a34a] text-black"
            >
              <Send className="w-4 h-4" />
            </motion.button>
          </form>
        </div>
      </div>
    </div>
  )
}

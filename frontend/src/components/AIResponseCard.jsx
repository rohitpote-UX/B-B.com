import { useState } from 'react'
import { Link } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import {
  ArrowRight, Trophy, Star, TrendingUp, TrendingDown, Shield,
  ThumbsUp, ThumbsDown, CheckCircle2, XCircle, Zap, Eye, MapPin,
  BadgeCheck, Sparkles, Youtube, MessageCircle, BarChart3,
  ChevronDown, ChevronRight, ExternalLink, ShoppingCart, Gamepad2,
  GraduationCap, Palette, Heart, BatteryFull, Camera, Globe
} from 'lucide-react'
import {
  AreaChart, Area, ResponsiveContainer, Tooltip, XAxis, YAxis
} from 'recharts'
import { formatPrice } from '../data/demoData'

// ── Animation variants ──
const fadeUp = {
  hidden: { opacity: 0, y: 16 },
  visible: (i = 0) => ({
    opacity: 1, y: 0,
    transition: { duration: 0.5, delay: i * 0.06, ease: [0.22, 1, 0.36, 1] }
  })
}

const COLORS = {
  green: '#22c55e', blue: '#3b82f6', purple: '#a855f7',
  amber: '#f59e0b', red: '#ef4444', cyan: '#06b6d4', pink: '#ec4899',
}

// ── Mini Tooltip for charts ──
function MiniTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null
  return (
    <div className="bg-theme-elevated border border-theme-border rounded-lg px-3 py-2 shadow-lg text-[0.7rem]">
      <p className="text-theme-muted">{label}</p>
      <p className="font-semibold text-theme-text">{formatPrice(payload[0].value)}</p>
    </div>
  )
}

// ── Sentiment Mini-Bar ──
function SentimentMini({ positive, neutral, negative, label, icon: Icon, iconColor }) {
  return (
    <div className="flex items-center gap-3">
      <Icon className="w-3.5 h-3.5 flex-shrink-0" style={{ color: iconColor }} />
      <div className="flex-1">
        <div className="flex items-center justify-between mb-1">
          <span className="text-[0.65rem] text-theme-muted">{label}</span>
          <span className="text-[0.6rem] font-medium text-[#22c55e]">{positive}%</span>
        </div>
        <div className="w-full h-1.5 rounded-full overflow-hidden flex bg-theme-subtle">
          <motion.div initial={{ width: 0 }} animate={{ width: `${positive}%` }}
            transition={{ duration: 0.8, delay: 0.2 }} className="h-full bg-[#22c55e]" />
          <motion.div initial={{ width: 0 }} animate={{ width: `${neutral}%` }}
            transition={{ duration: 0.8, delay: 0.35 }} className="h-full bg-[#f59e0b]" />
          <motion.div initial={{ width: 0 }} animate={{ width: `${negative}%` }}
            transition={{ duration: 0.8, delay: 0.5 }} className="h-full bg-[#ef4444]" />
        </div>
      </div>
    </div>
  )
}

// ── Product Badge ──
function Badge({ text }) {
  const isPositive = text.includes('Best') || text.includes('Top') || text.includes('Champion') || text.includes('Popular') || text.includes('Gem') || text.includes('Beast') || text.includes('Favorite') || text.includes('King') || text.includes('Pick')
  const isWarning = text.includes('Overpriced')
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-[0.55rem] font-bold uppercase tracking-wider border ${
      isWarning ? 'bg-[#ef444412] text-[#ef4444] border-[#ef444425]'
      : isPositive ? 'bg-[#22c55e12] text-[#22c55e] border-[#22c55e25]'
      : 'bg-[#3b82f612] text-[#3b82f6] border-[#3b82f625]'
    }`}>
      {text}
    </span>
  )
}

// ── Persona Fit Bar ──
function PersonaBar({ persona, delay = 0 }) {
  return (
    <div className={`flex items-center gap-2.5 ${persona.highlighted ? '' : 'opacity-70'}`}>
      <span className="text-[0.8rem]">{persona.label.split(' ')[0]}</span>
      <div className="flex-1 h-1.5 bg-theme-subtle rounded-full overflow-hidden">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${persona.score}%` }}
          transition={{ duration: 1, delay, ease: [0.22, 1, 0.36, 1] }}
          className="h-full rounded-full"
          style={{ background: persona.highlighted ? `linear-gradient(90deg, ${COLORS.green}, ${COLORS.cyan})` : COLORS.blue + '70' }}
        />
      </div>
      <span className={`text-[0.7rem] font-semibold ${persona.highlighted ? 'text-[#22c55e]' : 'text-theme-muted'}`}>
        {persona.score}%
      </span>
    </div>
  )
}

// ══════════════════════════════════════════════════════════════
// MAIN: AIResponseCard — Renders a structured AI response
// ══════════════════════════════════════════════════════════════

export default function AIResponseCard({ data }) {
  const [expandedSection, setExpandedSection] = useState(null)

  // Not Found response
  if (data.type === 'not_found') {
    return (
      <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="space-y-4">
        <div className="bg-theme-elevated border border-theme-border rounded-2xl p-6">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-8 h-8 rounded-xl bg-[#f59e0b15] border border-[#f59e0b25] flex items-center justify-center">
              <Eye className="w-4 h-4 text-[#f59e0b]" />
            </div>
            <p className="text-[0.85rem] text-theme-secondary leading-relaxed">{data.greeting}</p>
          </div>
          {data.detectedCategory && (
            <p className="text-[0.75rem] text-theme-dim mt-2">
              I detected you might be looking for <span className="text-theme-text font-medium">{data.detectedCategory}</span>, but couldn't find matches with your filters.
            </p>
          )}
          <p className="text-[0.75rem] text-theme-muted mt-3 italic">{data.suggestion}</p>
        </div>
      </motion.div>
    )
  }

  const { topPick, alternatives, greeting, detectedCategory, totalSearched } = data
  const product = topPick.product
  const pName = product.name.split('(')[0].trim()

  return (
    <div className="space-y-4">

      {/* ════ GREETING ════ */}
      <motion.div custom={0} variants={fadeUp} initial="hidden" animate="visible">
        <div className="bg-theme-elevated border border-theme-border rounded-2xl px-5 py-4">
          <p className="text-[0.85rem] text-theme-secondary leading-relaxed">{greeting}</p>
          <div className="flex items-center gap-3 mt-2">
            <span className="text-[0.6rem] text-theme-dim uppercase tracking-widest">
              Searched {totalSearched} {detectedCategory || 'products'} · AI Confidence: {data.confidence}
            </span>
          </div>
        </div>
      </motion.div>

      {/* ════ MARKET SIGNALS ════ */}
      {topPick.marketSignals.length > 0 && (
        <motion.div custom={1} variants={fadeUp} initial="hidden" animate="visible">
          <div className="flex flex-wrap gap-2">
            {topPick.marketSignals.map((signal, i) => (
              <motion.span
                key={i}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.3 + i * 0.1 }}
                className="px-3 py-1.5 rounded-full bg-gradient-to-r from-[#22c55e08] to-[#3b82f608] border border-[#22c55e20] text-[0.65rem] font-medium text-[#22c55e]"
              >
                {signal}
              </motion.span>
            ))}
          </div>
        </motion.div>
      )}

      {/* ════ TOP PICK HERO CARD ════ */}
      <motion.div custom={2} variants={fadeUp} initial="hidden" animate="visible">
        <div className="relative bg-theme-elevated border border-[#22c55e20] rounded-2xl overflow-hidden shadow-[0_0_30px_rgba(34,197,94,0.04)]">
          {/* Top glow line */}
          <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-[#22c55e40] to-transparent" />

          <div className="p-5 sm:p-6">
            {/* Badges row */}
            <div className="flex flex-wrap gap-1.5 mb-4">
              {product.badges?.map((b, i) => <Badge key={i} text={b} />)}
            </div>

            <div className="flex flex-col sm:flex-row gap-5">
              {/* Product Image */}
              <Link to={`/product/${product.id}`} className="flex-shrink-0 w-full sm:w-36 h-36 bg-white rounded-xl border border-theme-border flex items-center justify-center p-3 group">
                <img src={product.image} alt="" className="max-w-full max-h-full object-contain mix-blend-multiply group-hover:scale-110 transition-transform duration-500" />
              </Link>

              {/* Product Info */}
              <div className="flex-1 min-w-0">
                <p className="text-[0.65rem] font-bold uppercase tracking-[0.15em] text-theme-muted mb-1">{product.brand} · {product.category}</p>
                <Link to={`/product/${product.id}`} className="block">
                  <h3 className="text-[1rem] sm:text-[1.1rem] font-medium text-theme-text leading-snug mb-2 hover:text-[#22c55e] transition-colors line-clamp-2">{product.name}</h3>
                </Link>

                <div className="flex flex-wrap items-center gap-3 mb-3">
                  <span className="text-[1.25rem] font-bold text-[#22c55e]">{formatPrice(product.bestPrice)}</span>
                  {product.originalPrice > product.bestPrice && (
                    <span className="text-[0.8rem] text-theme-dim line-through">{formatPrice(product.originalPrice)}</span>
                  )}
                  {product.originalPrice > product.bestPrice && (
                    <span className="px-2 py-0.5 rounded-full bg-[#22c55e15] text-[#22c55e] text-[0.6rem] font-bold">
                      {Math.round((1 - product.bestPrice / product.originalPrice) * 100)}% OFF
                    </span>
                  )}
                </div>

                <div className="flex items-center gap-4 text-[0.7rem] text-theme-secondary">
                  <div className="flex items-center gap-1"><Star className="w-3 h-3 fill-current text-amber-400" /><span>{product.rating}/5</span></div>
                  <div className="flex items-center gap-1"><TrendingUp className="w-3 h-3 text-[#22c55e]" /><span>Score {product.dealScore}</span></div>
                  <span className="text-theme-dim">{product.totalReviews.toLocaleString()} reviews</span>
                </div>
              </div>
            </div>

            {/* ── Why Recommended ── */}
            <div className="mt-5 pt-4 border-t border-theme-border">
              <div className="flex items-center gap-2 mb-2">
                <Sparkles className="w-3.5 h-3.5 text-[#a855f7]" />
                <span className="text-[0.65rem] font-bold uppercase tracking-[0.15em] text-[#a855f7]">Why This Is Recommended</span>
              </div>
              <p className="text-[0.8rem] text-theme-secondary leading-relaxed">{topPick.whyRecommended}</p>
            </div>

            {/* ── Deal Scanner ── */}
            {topPick.dealAnalysis && (
              <div className="mt-4 pt-4 border-t border-theme-border">
                <div className="flex items-center gap-2 mb-3">
                  <Zap className="w-3.5 h-3.5 text-[#22c55e]" />
                  <span className="text-[0.65rem] font-bold uppercase tracking-[0.15em] text-[#22c55e]">Deal Scanner</span>
                </div>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                  {topPick.dealAnalysis.platforms.map((p, i) => (
                    <div key={i} className={`px-3 py-2 rounded-lg border ${i === 0 ? 'border-[#22c55e30] bg-[#22c55e05]' : 'border-theme-border bg-theme-bg'}`}>
                      <div className="flex items-center gap-1.5 mb-1">
                        <span className="text-[0.8rem]">{p.icon}</span>
                        <span className="text-[0.6rem] font-medium text-theme-muted truncate">{p.name}</span>
                      </div>
                      <p className={`text-[0.85rem] font-bold ${i === 0 ? 'text-[#22c55e]' : 'text-theme-text'}`}>{formatPrice(p.price)}</p>
                    </div>
                  ))}
                </div>
                {topPick.dealAnalysis.savingsPercent > 0 && (
                  <p className="text-[0.7rem] text-[#22c55e] mt-2">
                    💰 Save {formatPrice(topPick.dealAnalysis.savings)} ({topPick.dealAnalysis.savingsPercent}%) by buying from {topPick.dealAnalysis.platforms[0].name}
                  </p>
                )}
              </div>
            )}

            {/* ── Quick Actions ── */}
            <div className="flex flex-wrap gap-2 mt-4 pt-4 border-t border-theme-border">
              <Link to={`/product/${product.id}`} className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-[#22c55e] text-black text-[0.65rem] font-bold uppercase tracking-widest hover:bg-[#16a34a] transition-colors">
                <ShoppingCart className="w-3 h-3" /> View Details
              </Link>
              <Link to={`/compare?p1=${product.id}`} className="flex items-center gap-1.5 px-4 py-2 rounded-xl border border-theme-border text-[0.65rem] font-bold uppercase tracking-widest text-theme-muted hover:text-theme-text hover:border-theme-strong transition-colors">
                <BarChart3 className="w-3 h-3" /> Compare
              </Link>
            </div>
          </div>
        </div>
      </motion.div>

      {/* ════ BEST FOR YOU — Persona Fit ════ */}
      <motion.div custom={3} variants={fadeUp} initial="hidden" animate="visible">
        <CollapsibleSection
          title="BEST FOR YOU"
          subtitle="AI persona matching"
          icon={Heart}
          iconColor={COLORS.pink}
          defaultOpen={true}
          id="persona"
          expanded={expandedSection}
          setExpanded={setExpandedSection}
        >
          <div className="space-y-3">
            {topPick.personaFit.map((persona, i) => (
              <PersonaBar key={persona.key} persona={persona} delay={i * 0.1} />
            ))}
          </div>
        </CollapsibleSection>
      </motion.div>

      {/* ════ COMMUNITY OPINION ════ */}
      <motion.div custom={4} variants={fadeUp} initial="hidden" animate="visible">
        <CollapsibleSection
          title="COMMUNITY OPINION"
          subtitle="YouTube · Reddit · Reviews"
          icon={MessageCircle}
          iconColor={COLORS.amber}
          id="sentiment"
          expanded={expandedSection}
          setExpanded={setExpandedSection}
        >
          <div className="space-y-3">
            <SentimentMini {...topPick.sentiment.youtube} label="YouTube" icon={Youtube} iconColor="#ef4444" />
            <SentimentMini {...topPick.sentiment.reddit} label="Reddit" icon={MessageCircle} iconColor="#f97316" />
            <SentimentMini {...topPick.sentiment.reviews} label="Reviews" icon={Star} iconColor="#f59e0b" />
          </div>
          <div className="flex items-center gap-3 mt-3 pt-3 border-t border-theme-border text-[0.55rem] text-theme-dim">
            <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-[#22c55e]" /> Positive</span>
            <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-[#f59e0b]" /> Neutral</span>
            <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-[#ef4444]" /> Negative</span>
          </div>
        </CollapsibleSection>
      </motion.div>

      {/* ════ PROS & CONS ════ */}
      <motion.div custom={5} variants={fadeUp} initial="hidden" animate="visible">
        <CollapsibleSection
          title="HONEST PROS & CONS"
          subtitle="AI-curated analysis"
          icon={Shield}
          iconColor={COLORS.green}
          id="proscons"
          expanded={expandedSection}
          setExpanded={setExpandedSection}
        >
          <div className="space-y-2 mb-4">
            <p className="text-[0.6rem] font-bold uppercase tracking-[0.2em] text-[#22c55e] mb-2">✓ Strengths</p>
            {topPick.prosAndCons.pros.map((pro, i) => (
              <motion.div key={i} initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.1 * i }}
                className="flex items-start gap-2">
                <CheckCircle2 className="w-3.5 h-3.5 text-[#22c55e] mt-0.5 flex-shrink-0" />
                <span className="text-[0.75rem] text-theme-secondary">{pro}</span>
              </motion.div>
            ))}
          </div>
          <div className="space-y-2">
            <p className="text-[0.6rem] font-bold uppercase tracking-[0.2em] text-[#ef4444] mb-2">✗ Weaknesses</p>
            {topPick.prosAndCons.cons.map((con, i) => (
              <motion.div key={i} initial={{ opacity: 0, x: 10 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.1 * i }}
                className="flex items-start gap-2">
                <XCircle className="w-3.5 h-3.5 text-[#ef4444] mt-0.5 flex-shrink-0" />
                <span className="text-[0.75rem] text-theme-secondary">{con}</span>
              </motion.div>
            ))}
          </div>
        </CollapsibleSection>
      </motion.div>

      {/* ════ PRICE HISTORY ════ */}
      <motion.div custom={6} variants={fadeUp} initial="hidden" animate="visible">
        <CollapsibleSection
          title="PRICE HISTORY"
          subtitle="6-month trend"
          icon={TrendingUp}
          iconColor={COLORS.cyan}
          id="price"
          expanded={expandedSection}
          setExpanded={setExpandedSection}
        >
          <div className="h-40 -mx-2">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={topPick.priceHistory}>
                <defs>
                  <linearGradient id="priceGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor={COLORS.green} stopOpacity={0.3} />
                    <stop offset="100%" stopColor={COLORS.green} stopOpacity={0} />
                  </linearGradient>
                </defs>
                <XAxis dataKey="month" tick={{ fill: '#666', fontSize: 10 }} axisLine={false} tickLine={false} />
                <YAxis hide domain={['auto', 'auto']} />
                <Tooltip content={<MiniTooltip />} />
                <Area type="monotone" dataKey="price" stroke={COLORS.green} fill="url(#priceGrad)" strokeWidth={2} dot={{ fill: COLORS.green, r: 3 }} animationDuration={1200} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
          <div className="flex items-center justify-between mt-2 text-[0.65rem]">
            <span className="text-theme-dim">Current: <span className="text-[#22c55e] font-semibold">{formatPrice(product.bestPrice)}</span></span>
            {product.originalPrice > product.bestPrice && (
              <span className="text-theme-dim">Original: <span className="line-through">{formatPrice(product.originalPrice)}</span></span>
            )}
          </div>
        </CollapsibleSection>
      </motion.div>

      {/* ════ ALTERNATIVE OPTIONS ════ */}
      {alternatives.length > 0 && (
        <motion.div custom={7} variants={fadeUp} initial="hidden" animate="visible">
          <div className="bg-theme-elevated border border-theme-border rounded-2xl overflow-hidden">
            <div className="px-5 py-3 border-b border-theme-border flex items-center gap-2">
              <Globe className="w-3.5 h-3.5 text-[#3b82f6]" />
              <span className="text-[0.65rem] font-bold uppercase tracking-[0.15em] text-[#3b82f6]">Alternative Options</span>
              <span className="text-[0.55rem] text-theme-dim ml-auto">{alternatives.length} more</span>
            </div>

            <div className="divide-y divide-theme-border">
              {alternatives.map((alt, i) => (
                <Link key={alt.product.id} to={`/product/${alt.product.id}`} className="flex items-center gap-4 px-5 py-4 hover:bg-theme-bg transition-colors group">
                  <div className="w-14 h-14 bg-white rounded-lg border border-theme-border flex items-center justify-center p-2 flex-shrink-0">
                    <img src={alt.product.image} alt="" className="max-w-full max-h-full object-contain mix-blend-multiply group-hover:scale-110 transition-transform duration-300" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex flex-wrap items-center gap-1.5 mb-1">
                      {alt.product.badges?.slice(0, 2).map((b, j) => <Badge key={j} text={b} />)}
                    </div>
                    <p className="text-[0.8rem] font-medium text-theme-text truncate group-hover:text-[#22c55e] transition-colors">{alt.product.name.split('(')[0].trim()}</p>
                    <div className="flex items-center gap-3 mt-0.5">
                      <span className="text-[0.8rem] font-bold text-theme-text">{formatPrice(alt.product.bestPrice)}</span>
                      <span className="text-[0.65rem] text-theme-dim flex items-center gap-1">
                        <Star className="w-2.5 h-2.5 fill-current text-amber-400" /> {alt.product.rating}
                      </span>
                      <span className="text-[0.65rem] text-theme-dim">Score {alt.product.dealScore}</span>
                    </div>
                    {alt.marketSignals?.[0] && (
                      <p className="text-[0.6rem] text-[#22c55e] mt-1">{alt.marketSignals[0]}</p>
                    )}
                  </div>
                  <ArrowRight className="w-4 h-4 text-theme-dim group-hover:text-theme-text transition-colors flex-shrink-0" />
                </Link>
              ))}
            </div>
          </div>
        </motion.div>
      )}

      {/* ════ AI FOOTER ════ */}
      <motion.div custom={8} variants={fadeUp} initial="hidden" animate="visible">
        <div className="flex items-center justify-center gap-2 py-2">
          <BadgeCheck className="w-3 h-3 text-[#22c55e]" />
          <span className="text-[0.55rem] text-theme-dim uppercase tracking-widest">
            Powered by BrandBattle AI · Your AI-Powered Buying Intelligence Platform
          </span>
        </div>
      </motion.div>
    </div>
  )
}


// ── Collapsible Section Component ──
function CollapsibleSection({ title, subtitle, icon: Icon, iconColor, children, defaultOpen = false, id, expanded, setExpanded }) {
  const isOpen = expanded === id || (expanded === null && defaultOpen)

  return (
    <div className="bg-theme-elevated border border-theme-border rounded-2xl overflow-hidden">
      <button
        onClick={() => setExpanded(isOpen ? null : id)}
        className="w-full px-5 py-3 flex items-center gap-3 hover:bg-theme-bg transition-colors"
      >
        <div className="w-7 h-7 rounded-lg flex items-center justify-center flex-shrink-0" style={{ background: `${iconColor}15`, border: `1px solid ${iconColor}25` }}>
          <Icon className="w-3.5 h-3.5" style={{ color: iconColor }} />
        </div>
        <div className="text-left flex-1 min-w-0">
          <span className="text-[0.65rem] font-bold uppercase tracking-[0.15em] text-theme-text block">{title}</span>
          {subtitle && <span className="text-[0.55rem] text-theme-dim">{subtitle}</span>}
        </div>
        <motion.div animate={{ rotate: isOpen ? 180 : 0 }} transition={{ duration: 0.3 }}>
          <ChevronDown className="w-4 h-4 text-theme-dim" />
        </motion.div>
      </button>
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="overflow-hidden"
          >
            <div className="px-5 pb-4 pt-1 border-t border-theme-border">
              {children}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

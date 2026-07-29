'use client'

import { useState, useMemo, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Trophy, Zap, Shield, Gamepad2, GraduationCap, Palette, Users,
  ThumbsUp, ThumbsDown, CheckCircle2, XCircle, Star, BadgeCheck, ChevronDown, Wrench,
  Smartphone, Wifi, ArrowUpRight, Sparkles, Eye,
  MessageCircle, Youtube, Globe, IndianRupee, DollarSign,
  Heart, Flame, Camera, BatteryFull, MapPin, CreditCard, Repeat,
  ShieldCheck, Lock, RefreshCw, Plug, Leaf, BarChart3, Activity,
  TrendingUp, TrendingDown
} from 'lucide-react'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, Legend,
  AreaChart, Area, PieChart, Pie, Cell
} from 'recharts'
import { generateDeepCompareData } from '@/data/deepCompareData'
import { formatPrice } from '@/data/demoData'
import { Product } from '@/types'

// -- Shared animation variants --
const sectionVariants = {
  hidden: { opacity: 0, y: 40 },
  visible: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: { duration: 0.7, delay: i * 0.1, ease: [0.22, 1, 0.36, 1] as any }
  })
}

// Color palette
const COLORS = {
  green: '#22c55e',
  greenDim: '#22c55e30',
  greenGlow: '#22c55e18',
  blue: '#3b82f6',
  blueDim: '#3b82f630',
  purple: '#a855f7',
  purpleDim: '#a855f730',
  amber: '#f59e0b',
  amberDim: '#f59e0b30',
  red: '#ef4444',
  redDim: '#ef444430',
  cyan: '#06b6d4',
  cyanDim: '#06b6d430',
  pink: '#ec4899',
  pinkDim: '#ec489930',
  glass: 'rgba(255,255,255,0.03)',
  glassBorder: 'rgba(255,255,255,0.08)',
}

const PIE_COLORS = ['#22c55e', '#3b82f6', '#f59e0b', '#a855f7', '#ef4444']

// -- Sub-components --

interface SectionHeaderProps {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  icon: any
  title: string
  subtitle?: string
  index: number
}

function SectionHeader({ icon: Icon, title, subtitle, index }: SectionHeaderProps) {
  return (
    <motion.div
      custom={index}
      variants={sectionVariants}
      initial="hidden"
      whileInView="visible"
      viewport={{ once: true, margin: "-50px" }}
      className="flex items-center gap-4 mb-10"
    >
      <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[#22c55e20] to-[#3b82f620] flex items-center justify-center border border-[#22c55e20]">
        <Icon className="w-5 h-5 text-[#22c55e]" />
      </div>
      <div>
        <h3 className="text-[0.7rem] font-bold uppercase tracking-[0.2em] text-theme-text">{title}</h3>
        {subtitle && <p className="text-[0.7rem] text-theme-muted mt-0.5">{subtitle}</p>}
      </div>
    </motion.div>
  )
}

interface GlassCardProps {
  children: React.ReactNode
  className?: string
  glow?: boolean
  winner?: boolean
}

function GlassCard({ children, className = '', glow = false, winner = false }: GlassCardProps) {
  return (
    <div className={`
      relative rounded-2xl border p-6 md:p-8 overflow-hidden transition-all duration-500
      ${winner
        ? 'border-[#22c55e30] bg-[#22c55e05] shadow-[0_0_40px_rgba(34,197,94,0.06)]'
        : 'border-theme-border bg-theme-elevated/50'}
      ${glow ? 'shadow-[0_0_60px_rgba(34,197,94,0.08)]' : ''}
      ${className}
    `}>
      {winner && (
        <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-[#22c55e50] to-transparent" />
      )}
      {children}
    </div>
  )
}

interface MetricBarProps {
  label: string
  value: number
  maxValue?: number
  winner?: boolean
  delay?: number
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  icon?: any
  color?: string
}

function MetricBar({ label, value, maxValue = 100, winner = false, delay = 0, icon: Icon, color = COLORS.green }: MetricBarProps) {
  const pct = Math.min((value / maxValue) * 100, 100)
  return (
    <div className="mb-5 last:mb-0">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          {Icon && <Icon className="w-3.5 h-3.5" style={{ color }} />}
          <span className="text-[0.75rem] text-theme-secondary">{label}</span>
        </div>
        <span className={`text-[0.8rem] font-semibold ${winner ? 'text-[#22c55e]' : 'text-theme-text'}`}>
          {value}/100
          {winner && <span className="ml-1.5 text-[0.6rem]">★</span>}
        </span>
      </div>
      <div className="w-full h-2 bg-theme-subtle rounded-full overflow-hidden">
        <motion.div
          initial={{ width: 0 }}
          whileInView={{ width: `${pct}%` }}
          viewport={{ once: true }}
          transition={{ duration: 1.2, delay, ease: [0.22, 1, 0.36, 1] }}
          className="h-full rounded-full"
          style={{
            background: winner
              ? `linear-gradient(90deg, ${color}, ${COLORS.green})`
              : `linear-gradient(90deg, ${color}90, ${color}50)`
          }}
        />
      </div>
    </div>
  )
}

interface SentimentBarProps {
  positive: number
  neutral: number
  negative: number
  label: string
  delay?: number
}

function SentimentBar({ positive, neutral, negative, label, delay = 0 }: SentimentBarProps) {
  return (
    <div className="mb-4 last:mb-0">
      <div className="flex items-center justify-between mb-2">
        <span className="text-[0.75rem] text-theme-secondary">{label}</span>
        <span className="text-[0.65rem] text-theme-muted">{positive}% positive</span>
      </div>
      <div className="w-full h-3 rounded-full overflow-hidden flex">
        <motion.div
          initial={{ width: 0 }}
          whileInView={{ width: `${positive}%` }}
          viewport={{ once: true }}
          transition={{ duration: 1, delay, ease: [0.22, 1, 0.36, 1] }}
          className="h-full bg-[#22c55e]"
        />
        <motion.div
          initial={{ width: 0 }}
          whileInView={{ width: `${neutral}%` }}
          viewport={{ once: true }}
          transition={{ duration: 1, delay: delay + 0.15, ease: [0.22, 1, 0.36, 1] }}
          className="h-full bg-[#f59e0b]"
        />
        <motion.div
          initial={{ width: 0 }}
          whileInView={{ width: `${negative}%` }}
          viewport={{ once: true }}
          transition={{ duration: 1, delay: delay + 0.3, ease: [0.22, 1, 0.36, 1] }}
          className="h-full bg-[#ef4444]"
        />
      </div>
    </div>
  )
}

interface ProConItemProps {
  text: string
  isPro: boolean
  delay?: number
}

function ProConItem({ text, isPro, delay = 0 }: ProConItemProps) {
  return (
    <motion.div
      initial={{ opacity: 0, x: isPro ? -20 : 20 }}
      whileInView={{ opacity: 1, x: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.5, delay }}
      className="flex items-start gap-3 py-3 border-b border-theme-border last:border-b-0"
    >
      {isPro
        ? <CheckCircle2 className="w-4 h-4 text-[#22c55e] mt-0.5 flex-shrink-0" />
        : <XCircle className="w-4 h-4 text-[#ef4444] mt-0.5 flex-shrink-0" />
      }
      <span className="text-[0.8rem] text-theme-secondary leading-relaxed">{text}</span>
    </motion.div>
  )
}

// Custom tooltip for charts
// eslint-disable-next-line @typescript-eslint/no-explicit-any
function CustomTooltip({ active, payload, label }: any) {
  if (!active || !payload?.length) return null
  return (
    <div className="bg-theme-elevated border border-theme-border rounded-lg px-4 py-3 shadow-xl">
      <p className="text-[0.7rem] font-medium text-theme-muted mb-1">{label}</p>
      {/* eslint-disable-next-line @typescript-eslint/no-explicit-any */}
      {payload.map((p: any, i: number) => (
        <p key={i} className="text-[0.8rem] font-semibold" style={{ color: p.color }}>
          {p.name}: {typeof p.value === 'number' ? (p.value > 10 ? formatPrice(p.value) : p.value) : p.value}
        </p>
      ))}
    </div>
  )
}

// -- Main Component --

interface DeepCompareProps {
  product1: Product
  product2: Product
  winnerIndex: number | null
}

export default function DeepCompare({ product1, product2, winnerIndex }: DeepCompareProps) {
  const [regionTab, setRegionTab] = useState('india')
  const data = useMemo(
    () => generateDeepCompareData(product1, product2, winnerIndex) as any,
    [product1.id, product2.id, winnerIndex]
  )

  const p1Name = product1.name.split('(')[0].trim()
  const p2Name = product2.name.split('(')[0].trim()
  const winnerProduct = winnerIndex !== null ? (winnerIndex === 0 ? product1 : product2) : null
  const winnerName = winnerProduct ? winnerProduct.name.split('(')[0].trim() : null

  // Prepare radar chart data
  const radarData = [
    { subject: 'Gaming', p1: data.personaScores.product1.gamer, p2: data.personaScores.product2.gamer },
    { subject: 'Student', p1: data.personaScores.product1.student, p2: data.personaScores.product2.student },
    { subject: 'Creator', p1: data.personaScores.product1.creator, p2: data.personaScores.product2.creator },
    { subject: 'Parent', p1: data.personaScores.product1.parent, p2: data.personaScores.product2.parent },
  ]

  // Prepare price history data
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const priceHistoryData = data.priceHistory.product1.map((p: any, i: number) => ({
    month: p.month,
    [p1Name.slice(0, 20)]: p.price,
    [p2Name.slice(0, 20)]: data.priceHistory.product2[i].price,
  }))

  // Scoring pie data
  const scoringPieData = [
    { name: 'Price', value: 30 },
    { name: 'Rating', value: 25 },
    { name: 'Deal Score', value: 20 },
    { name: 'Reviews', value: 15 },
    { name: 'Brand', value: 10 },
  ]

  // Performance bar chart data
  const perfData = [
    { name: 'Battery', p1: data.realWorldPerformance.product1.battery, p2: data.realWorldPerformance.product2.battery },
    { name: 'Thermal', p1: data.realWorldPerformance.product1.heating, p2: data.realWorldPerformance.product2.heating },
    { name: 'Gaming', p1: data.realWorldPerformance.product1.gaming, p2: data.realWorldPerformance.product2.gaming },
    { name: 'Camera', p1: data.realWorldPerformance.product1.camera, p2: data.realWorldPerformance.product2.camera },
  ]

  return (
    <div className="mt-2">
      {/* ═══════ STICKY COMPARISON HEADER ═══════ */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="sticky top-20 z-30 mb-12"
      >
        <div className="bg-theme-bg/80 backdrop-blur-xl border border-theme-border rounded-2xl px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-white rounded-lg p-1 border border-theme-border">
              <img src={product1.image} alt={p1Name} className="w-full h-full object-contain mix-blend-multiply" />
            </div>
            <span className="text-[0.75rem] font-medium text-theme-text hidden sm:block">{p1Name.slice(0, 25)}</span>
          </div>
          <div className="flex items-center gap-2 px-4">
            <Sparkles className="w-4 h-4 text-[#a855f7]" />
            <span className="text-[0.65rem] font-bold uppercase tracking-[0.2em] text-[#a855f7]">AI Deep Analysis</span>
          </div>
          <div className="flex items-center gap-3">
            <span className="text-[0.75rem] font-medium text-theme-text hidden sm:block">{p2Name.slice(0, 25)}</span>
            <div className="w-8 h-8 bg-white rounded-lg p-1 border border-theme-border">
              <img src={product2.image} alt={p2Name} className="w-full h-full object-contain mix-blend-multiply" />
            </div>
          </div>
        </div>
      </motion.div>

      {/* ═══════ 1. AI VERDICT BANNER ═══════ */}
      <motion.div
        custom={0}
        variants={sectionVariants}
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true }}
        className="mb-16"
      >
        <div className="relative rounded-3xl overflow-hidden border border-[#22c55e20]">
          {/* Animated gradient background */}
          <div className="absolute inset-0 bg-gradient-to-br from-[#22c55e08] via-[#3b82f605] to-[#a855f708]" />
          <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-[#22c55e40] to-transparent" />
          <div className="absolute bottom-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-[#3b82f640] to-transparent" />

          <div className="relative px-8 py-16 md:px-16 md:py-20 text-center">
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ type: 'spring', stiffness: 200, damping: 20, delay: 0.3 }}
              className="w-16 h-16 mx-auto mb-8 rounded-2xl bg-gradient-to-br from-[#22c55e20] to-[#3b82f620] flex items-center justify-center border border-[#22c55e30]"
            >
              <Trophy className="w-8 h-8 text-[#22c55e]" />
            </motion.div>

            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.5 }}
              className="text-[0.65rem] font-bold uppercase tracking-[0.25em] text-[#22c55e] mb-4"
            >
              AI-Powered Verdict • {data.verdict.confidence}% Confidence
            </motion.p>

            <motion.h2
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6, duration: 0.8 }}
              className="text-[2rem] md:text-[3rem] font-[var(--font-display)] font-medium tracking-tight text-theme-text mb-4"
            >
              {winnerName ? (
                <>
                  <span className="text-[#22c55e]">{winnerName}</span>
                  <br />
                  <span className="text-theme-muted text-[1.5rem] md:text-[2rem]">is the {data.verdict.primary}</span>
                </>
              ) : (
                <span className="text-theme-muted">It&apos;s a Close Call</span>
              )}
            </motion.h2>

            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.9 }}
              className="flex items-center justify-center gap-6 mt-8"
            >
              <span className="px-4 py-1.5 rounded-full bg-[#22c55e15] border border-[#22c55e25] text-[0.65rem] font-bold uppercase tracking-widest text-[#22c55e]">
                {data.verdict.primary}
              </span>
              {data.verdict.secondary && (
                <span className="px-4 py-1.5 rounded-full bg-[#3b82f615] border border-[#3b82f625] text-[0.65rem] font-bold uppercase tracking-widest text-[#3b82f6]">
                  Runner-up: {data.verdict.secondary}
                </span>
              )}
            </motion.div>

            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 1.1 }}
              className="flex items-center justify-center gap-2 mt-6"
            >
              <BadgeCheck className="w-4 h-4 text-[#22c55e]" />
              <span className="text-[0.65rem] text-theme-muted">Verified by BrandBattle AI • AI-Powered Buying Intelligence Platform</span>
            </motion.div>
          </div>
        </div>
      </motion.div>

      {/* ═══════ 2. WHY THIS WON ═══════ */}
      <div className="mb-16">
        <SectionHeader icon={Eye} title="WHY THIS WON" subtitle="AI-generated analysis of each product's strengths" index={1} />
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {[
            { product: product1, narrative: data.whyThisWon.product1, isWinner: winnerIndex === 0 },
            { product: product2, narrative: data.whyThisWon.product2, isWinner: winnerIndex === 1 },
          ].map((item, i) => (
            <motion.div
              key={i}
              custom={2 + i}
              variants={sectionVariants}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true }}
            >
              <GlassCard winner={item.isWinner}>
                <div className="flex items-center gap-3 mb-5">
                  <div className="w-10 h-10 bg-white rounded-xl p-1.5 border border-theme-border">
                    <img src={item.product.image} alt={item.product.name} className="w-full h-full object-contain mix-blend-multiply" />
                  </div>
                  <div>
                    <p className="text-[0.75rem] font-medium text-theme-text">{item.product.name.split('(')[0].trim()}</p>
                    <p className="text-[0.6rem] text-theme-muted">{item.product.brand}</p>
                  </div>
                  {item.isWinner && (
                    <motion.div
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      transition={{ type: 'spring', delay: 0.5 }}
                      className="ml-auto"
                    >
                      <Trophy className="w-5 h-5 text-[#22c55e]" />
                    </motion.div>
                  )}
                </div>
                <p className="text-[0.85rem] leading-[1.8] text-theme-secondary">{item.narrative}</p>
              </GlassCard>
            </motion.div>
          ))}
        </div>
      </div>

      {/* ═══════ 3. USER PERSONA RADAR CHART ═══════ */}
      <div className="mb-16">
        <SectionHeader icon={Users} title="WHO SHOULD BUY THIS?" subtitle="AI recommendations for different user profiles" index={4} />
        <motion.div
          custom={5}
          variants={sectionVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
        >
          <GlassCard>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-center">
              {/* Radar Chart */}
              <div className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <RadarChart data={radarData}>
                    <PolarGrid stroke="#333" strokeDasharray="3 3" />
                    <PolarAngleAxis
                      dataKey="subject"
                      tick={{ fill: '#999', fontSize: 11, fontWeight: 600 }}
                    />
                    <PolarRadiusAxis
                      angle={90}
                      domain={[0, 100]}
                      tick={{ fill: '#555', fontSize: 9 }}
                    />
                    <Radar
                      name={p1Name.slice(0, 18)}
                      dataKey="p1"
                      stroke={COLORS.green}
                      fill={COLORS.green}
                      fillOpacity={0.15}
                      strokeWidth={2}
                    />
                    <Radar
                      name={p2Name.slice(0, 18)}
                      dataKey="p2"
                      stroke={COLORS.blue}
                      fill={COLORS.blue}
                      fillOpacity={0.15}
                      strokeWidth={2}
                    />
                    <Legend
                      wrapperStyle={{ fontSize: '11px', fontWeight: 500 }}
                    />
                  </RadarChart>
                </ResponsiveContainer>
              </div>

              {/* Persona Breakdown */}
              <div className="space-y-6">
                {[
                  { icon: Gamepad2, label: 'Gamers', k: 'gamer', color: COLORS.purple, desc: 'Frame rates, thermals, performance' },
                  { icon: GraduationCap, label: 'Students', k: 'student', color: COLORS.blue, desc: 'Battery, price, productivity' },
                  { icon: Palette, label: 'Creators', k: 'creator', color: COLORS.pink, desc: 'Camera, display, editing power' },
                  { icon: Heart, label: 'Parents', k: 'parent', color: COLORS.amber, desc: 'Safety, price, durability' },
                ].map((persona) => {
                  const v1 = data.personaScores.product1[persona.k]
                  const v2 = data.personaScores.product2[persona.k]
                  const w1 = v1 > v2
                  const w2 = v2 > v1
                  return (
                    <div key={persona.k} className="flex items-center gap-4">
                      <div className="w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0" style={{ background: `${persona.color}15`, border: `1px solid ${persona.color}25` }}>
                        <persona.icon className="w-4 h-4" style={{ color: persona.color }} />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between mb-1">
                          <span className="text-[0.75rem] font-medium text-theme-text">{persona.label}</span>
                          <div className="flex items-center gap-3 text-[0.7rem]">
                            <span className={w1 ? 'font-bold text-[#22c55e]' : 'text-theme-muted'}>{v1}</span>
                            <span className="text-theme-dim">vs</span>
                            <span className={w2 ? 'font-bold text-[#22c55e]' : 'text-theme-muted'}>{v2}</span>
                          </div>
                        </div>
                        <p className="text-[0.65rem] text-theme-dim">{persona.desc}</p>
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          </GlassCard>
        </motion.div>
      </div>

      {/* ═══════ 4. REAL-WORLD PERFORMANCE HISTOGRAM ═══════ */}
      <div className="mb-16">
        <SectionHeader icon={Activity} title="REAL-WORLD PERFORMANCE" subtitle="Simulated benchmarks based on brand DNA and user feedback" index={6} />
        <motion.div
          custom={7}
          variants={sectionVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
        >
          <GlassCard>
            <div className="h-80 mb-6">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={perfData} barGap={4} barCategoryGap="20%">
                  <CartesianGrid strokeDasharray="3 3" stroke="#222" vertical={false} />
                  <XAxis
                    dataKey="name"
                    tick={{ fill: '#999', fontSize: 11, fontWeight: 600 }}
                    axisLine={{ stroke: '#333' }}
                  />
                  <YAxis
                    domain={[0, 100]}
                    tick={{ fill: '#555', fontSize: 10 }}
                    axisLine={{ stroke: '#333' }}
                  />
                  <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(255,255,255,0.03)' }} />
                  <Bar
                    dataKey="p1"
                    name={p1Name.slice(0, 18)}
                    fill={COLORS.green}
                    radius={[6, 6, 0, 0]}
                  />
                  <Bar
                    dataKey="p2"
                    name={p2Name.slice(0, 18)}
                    fill={COLORS.blue}
                    radius={[6, 6, 0, 0]}
                  />
                  <Legend wrapperStyle={{ fontSize: '11px', fontWeight: 500, paddingTop: '12px' }} />
                </BarChart>
              </ResponsiveContainer>
            </div>

            {/* Side-by-side metric bars */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mt-8 pt-8 border-t border-theme-border">
              {[
                { label: p1Name.slice(0, 22), perf: data.realWorldPerformance.product1, isWinner: winnerIndex === 0 },
                { label: p2Name.slice(0, 22), perf: data.realWorldPerformance.product2, isWinner: winnerIndex === 1 },
              ].map((side, si) => (
                <div key={si}>
                  <p className="text-[0.7rem] font-bold uppercase tracking-[0.15em] text-theme-muted mb-5">{side.label}</p>
                  <MetricBar label="Battery Backup" value={side.perf.battery} icon={BatteryFull} color={COLORS.green}
                    winner={side.perf.battery > (si === 0 ? data.realWorldPerformance.product2.battery : data.realWorldPerformance.product1.battery)} delay={0.1} />
                  <MetricBar label="Thermal Control" value={side.perf.heating} icon={Flame} color={COLORS.amber}
                    winner={side.perf.heating > (si === 0 ? data.realWorldPerformance.product2.heating : data.realWorldPerformance.product1.heating)} delay={0.2} />
                  <MetricBar label="Gaming Performance" value={side.perf.gaming} icon={Gamepad2} color={COLORS.purple}
                    winner={side.perf.gaming > (si === 0 ? data.realWorldPerformance.product2.gaming : data.realWorldPerformance.product1.gaming)} delay={0.3} />
                  <MetricBar label="Camera Quality" value={side.perf.camera} icon={Camera} color={COLORS.blue}
                    winner={side.perf.camera > (si === 0 ? data.realWorldPerformance.product2.camera : data.realWorldPerformance.product1.camera)} delay={0.4} />
                </div>
              ))}
            </div>
          </GlassCard>
        </motion.div>
      </div>

      {/* ═══════ 5. REGION INTELLIGENCE TABS ═══════ */}
      <div className="mb-16">
        <SectionHeader icon={Globe} title="REGION-SPECIFIC INTELLIGENCE" subtitle="Tailored insights for your market" index={8} />

        {/* Tabs */}
        <div className="flex items-center gap-2 mb-8">
          {[
            { id: 'india', label: '🇮🇳 India / Asia', icon: IndianRupee },
            { id: 'usa', label: '🇺🇸 USA / Global', icon: DollarSign },
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setRegionTab(tab.id)}
              className={`
                px-5 py-2.5 rounded-xl text-[0.7rem] font-bold uppercase tracking-[0.15em] transition-all duration-300
                ${regionTab === tab.id
                  ? 'bg-[#22c55e15] text-[#22c55e] border border-[#22c55e30]'
                  : 'bg-theme-elevated text-theme-muted border border-theme-border hover:text-theme-text'}
              `}
            >
              {tab.label}
            </button>
          ))}
        </div>

        <AnimatePresence mode="wait">
          {regionTab === 'india' ? (
            <motion.div
              key="india"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.4 }}
            >
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {[
                  { product: product1, intel: data.indiaIntel.product1, isWinner: winnerIndex === 0 },
                  { product: product2, intel: data.indiaIntel.product2, isWinner: winnerIndex === 1 },
                ].map((side, si) => (
                  <GlassCard key={si} winner={side.isWinner}>
                    <p className="text-[0.7rem] font-bold uppercase tracking-[0.15em] text-theme-muted mb-6">{side.product.name.split('(')[0].trim()}</p>

                    {/* Service Centers */}
                    <div className="mb-6 pb-6 border-b border-theme-border">
                      <div className="flex items-center gap-2 mb-3">
                        <MapPin className="w-4 h-4 text-[#22c55e]" />
                        <span className="text-[0.75rem] font-medium text-theme-text">Service Center Network</span>
                      </div>
                      <MetricBar label={`${side.intel.serviceCenters.cities}+ cities covered`} value={side.intel.serviceCenters.score} icon={MapPin} color={COLORS.green} delay={0.1} />
                      <p className="text-[0.7rem] text-theme-dim mt-2">{side.intel.serviceCenters.note}</p>
                    </div>

                    {/* Motherboard / Green-line Issues */}
                    <div className="mb-6 pb-6 border-b border-theme-border">
                      <div className="flex items-center gap-2 mb-3">
                        <ShieldCheck className="w-4 h-4 text-[#3b82f6]" />
                        <span className="text-[0.75rem] font-medium text-theme-text">Hardware Reliability</span>
                        <span className={`text-[0.6rem] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full ml-auto ${
                          side.intel.motherboardIssues.riskLevel === 'Low Risk' ? 'bg-[#22c55e15] text-[#22c55e]'
                          : side.intel.motherboardIssues.riskLevel === 'Moderate' ? 'bg-[#f59e0b15] text-[#f59e0b]'
                          : 'bg-[#ef444415] text-[#ef4444]'
                        }`}>
                          {side.intel.motherboardIssues.riskLevel}
                        </span>
                      </div>
                      <MetricBar label="Reliability Score" value={side.intel.motherboardIssues.score} icon={Shield} color={COLORS.blue} delay={0.2} />
                      <p className="text-[0.7rem] text-theme-dim mt-2">{side.intel.motherboardIssues.note}</p>
                    </div>

                    {/* EMI Options */}
                    <div className="mb-6 pb-6 border-b border-theme-border">
                      <div className="flex items-center gap-2 mb-3">
                        <CreditCard className="w-4 h-4 text-[#a855f7]" />
                        <span className="text-[0.75rem] font-medium text-theme-text">EMI Options</span>
                        {side.intel.emiOptions.noCostEmi && (
                          <span className="text-[0.55rem] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full bg-[#22c55e15] text-[#22c55e] ml-auto">
                            No-Cost EMI ✓
                          </span>
                        )}
                      </div>
                      <p className="text-[0.8rem] text-theme-secondary">
                        Available on <span className="font-medium text-theme-text">{side.intel.emiOptions.banks}</span> bank cards •
                        Starting ₹{side.intel.emiOptions.minEmi}/mo
                      </p>
                      <p className="text-[0.7rem] text-theme-dim mt-1">{side.intel.emiOptions.note}</p>
                    </div>

                    {/* Exchange Offers */}
                    <div className="mb-6 pb-6 border-b border-theme-border">
                      <div className="flex items-center gap-2 mb-3">
                        <Repeat className="w-4 h-4 text-[#06b6d4]" />
                        <span className="text-[0.75rem] font-medium text-theme-text">Exchange Offers</span>
                      </div>
                      <p className="text-[0.8rem] text-theme-secondary">{side.intel.exchangeOffers.note}</p>
                    </div>

                    {/* Seller Trust */}
                    <div>
                      <div className="flex items-center gap-2 mb-3">
                        <Shield className="w-4 h-4 text-[#f59e0b]" />
                        <span className="text-[0.75rem] font-medium text-theme-text">Seller Trust Scores</span>
                      </div>
                      <div className="flex items-center gap-6">
                        <div>
                          <span className="text-[0.65rem] text-theme-muted">Amazon</span>
                          <p className="text-[1rem] font-bold text-theme-text">{side.intel.sellerTrust.amazon}<span className="text-[0.6rem] text-theme-dim">/100</span></p>
                        </div>
                        <div>
                          <span className="text-[0.65rem] text-theme-muted">Flipkart</span>
                          <p className="text-[1rem] font-bold text-theme-text">{side.intel.sellerTrust.flipkart}<span className="text-[0.6rem] text-theme-dim">/100</span></p>
                        </div>
                      </div>
                      <p className="text-[0.65rem] text-theme-dim mt-2">{side.intel.sellerTrust.note}</p>
                    </div>
                  </GlassCard>
                ))}
              </div>
            </motion.div>
          ) : (
            <motion.div
              key="usa"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.4 }}
            >
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {[
                  { product: product1, intel: data.usaIntel.product1, isWinner: winnerIndex === 0 },
                  { product: product2, intel: data.usaIntel.product2, isWinner: winnerIndex === 1 },
                ].map((side, si) => (
                  <GlassCard key={si} winner={side.isWinner}>
                    <p className="text-[0.7rem] font-bold uppercase tracking-[0.15em] text-theme-muted mb-6">{side.product.name.split('(')[0].trim()}</p>

                    {[
                      { icon: Lock, label: 'Privacy Score', metric: side.intel.privacy, color: COLORS.green },
                      { icon: RefreshCw, label: 'Software Updates', metric: side.intel.softwareUpdates, color: COLORS.blue },
                      { icon: Plug, label: 'Ecosystem Compatibility', metric: side.intel.ecosystem, color: COLORS.purple },
                      { icon: Wrench, label: 'Repairability Index', metric: side.intel.repairability, color: COLORS.amber },
                      { icon: TrendingUp, label: 'Resale Value', metric: side.intel.resaleValue, color: COLORS.cyan },
                      { icon: Leaf, label: 'Sustainability', metric: side.intel.sustainability, color: COLORS.pink },
                    ].map((item, idx) => (
                      <div key={idx} className={`${idx < 5 ? 'mb-5 pb-5 border-b border-theme-border' : ''}`}>
                        <div className="flex items-center gap-2 mb-2">
                          <item.icon className="w-4 h-4" style={{ color: item.color }} />
                          <span className="text-[0.75rem] font-medium text-theme-text">{item.label}</span>
                          <span className="ml-auto text-[0.6rem] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full"
                            style={{
                              background: item.metric.score > 75 ? COLORS.greenDim : item.metric.score > 55 ? COLORS.amberDim : COLORS.redDim,
                              color: item.metric.score > 75 ? COLORS.green : item.metric.score > 55 ? COLORS.amber : COLORS.red
                            }}>
                            {item.metric.score}/100
                          </span>
                        </div>
                        <MetricBar label="" value={item.metric.score} color={item.color} delay={idx * 0.08} />
                        <p className="text-[0.7rem] text-theme-dim mt-1">{item.metric.note}</p>
                      </div>
                    ))}
                  </GlassCard>
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* ═══════ 6. COMMUNITY SENTIMENT ═══════ */}
      <div className="mb-16">
        <SectionHeader icon={MessageCircle} title="COMMUNITY SENTIMENT ANALYSIS" subtitle="Aggregated from YouTube, Reddit, and verified reviews" index={10} />
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {[
            { product: product1, sentiment: data.sentiment.product1, isWinner: winnerIndex === 0 },
            { product: product2, sentiment: data.sentiment.product2, isWinner: winnerIndex === 1 },
          ].map((side, si) => (
            <motion.div
              key={si}
              custom={11 + si}
              variants={sectionVariants}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true }}
            >
              <GlassCard winner={side.isWinner}>
                <p className="text-[0.7rem] font-bold uppercase tracking-[0.15em] text-theme-muted mb-6">{side.product.name.split('(')[0].trim()}</p>

                <div className="space-y-5">
                  <div>
                    <div className="flex items-center gap-2 mb-2">
                      <Youtube className="w-4 h-4 text-[#ef4444]" />
                      <span className="text-[0.7rem] font-medium text-theme-text">YouTube Reviews</span>
                    </div>
                    <SentimentBar
                      positive={side.sentiment.youtube.positive}
                      neutral={side.sentiment.youtube.neutral}
                      negative={side.sentiment.youtube.negative}
                      label=""
                      delay={0.1}
                    />
                  </div>

                  <div>
                    <div className="flex items-center gap-2 mb-2">
                      <MessageCircle className="w-4 h-4 text-[#f97316]" />
                      <span className="text-[0.7rem] font-medium text-theme-text">Reddit Discussions</span>
                    </div>
                    <SentimentBar
                      positive={side.sentiment.reddit.positive}
                      neutral={side.sentiment.reddit.neutral}
                      negative={side.sentiment.reddit.negative}
                      label=""
                      delay={0.2}
                    />
                  </div>

                  <div>
                    <div className="flex items-center gap-2 mb-2">
                      <Star className="w-4 h-4 text-[#f59e0b]" />
                      <span className="text-[0.7rem] font-medium text-theme-text">Verified Reviews</span>
                    </div>
                    <SentimentBar
                      positive={side.sentiment.reviews.positive}
                      neutral={side.sentiment.reviews.neutral}
                      negative={side.sentiment.reviews.negative}
                      label=""
                      delay={0.3}
                    />
                  </div>
                </div>

                {/* Sentiment legend */}
                <div className="flex items-center gap-4 mt-5 pt-4 border-t border-theme-border">
                  <div className="flex items-center gap-1.5"><div className="w-2.5 h-2.5 rounded-full bg-[#22c55e]" /><span className="text-[0.6rem] text-theme-dim">Positive</span></div>
                  <div className="flex items-center gap-1.5"><div className="w-2.5 h-2.5 rounded-full bg-[#f59e0b]" /><span className="text-[0.6rem] text-theme-dim">Neutral</span></div>
                  <div className="flex items-center gap-1.5"><div className="w-2.5 h-2.5 rounded-full bg-[#ef4444]" /><span className="text-[0.6rem] text-theme-dim">Negative</span></div>
                </div>
              </GlassCard>
            </motion.div>
          ))}
        </div>
      </div>

      {/* ═══════ 7. HISTORICAL PRICE TRACKING ═══════ */}
      <div className="mb-16">
        <SectionHeader icon={TrendingUp} title="PRICE HISTORY TRACKER" subtitle="6-month price trend across platforms" index={13} />
        <motion.div
          custom={14}
          variants={sectionVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
        >
          <GlassCard>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={priceHistoryData}>
                  <defs>
                    <linearGradient id="gradP1" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor={COLORS.green} stopOpacity={0.3} />
                      <stop offset="100%" stopColor={COLORS.green} stopOpacity={0} />
                    </linearGradient>
                    <linearGradient id="gradP2" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor={COLORS.blue} stopOpacity={0.3} />
                      <stop offset="100%" stopColor={COLORS.blue} stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#222" vertical={false} />
                  <XAxis
                    dataKey="month"
                    tick={{ fill: '#999', fontSize: 11, fontWeight: 500 }}
                    axisLine={{ stroke: '#333' }}
                  />
                  <YAxis
                    tick={{ fill: '#555', fontSize: 10 }}
                    axisLine={{ stroke: '#333' }}
                    tickFormatter={(v) => `$${v}`}
                  />
                  <Tooltip content={<CustomTooltip />} />
                  <Area
                    type="monotone"
                    dataKey={p1Name.slice(0, 20)}
                    stroke={COLORS.green}
                    fill="url(#gradP1)"
                    strokeWidth={2.5}
                    dot={{ fill: COLORS.green, r: 4 }}
                  />
                  <Area
                    type="monotone"
                    dataKey={p2Name.slice(0, 20)}
                    stroke={COLORS.blue}
                    fill="url(#gradP2)"
                    strokeWidth={2.5}
                    dot={{ fill: COLORS.blue, r: 4 }}
                  />
                  <Legend wrapperStyle={{ fontSize: '11px', fontWeight: 500, paddingTop: '12px' }} />
                </AreaChart>
              </ResponsiveContainer>
            </div>

            <div className="grid grid-cols-2 gap-6 mt-6 pt-6 border-t border-theme-border">
              {[
                { product: product1, color: COLORS.green },
                { product: product2, color: COLORS.blue },
              ].map((side, si) => {
                const savings = side.product.originalPrice - side.product.bestPrice
                const savingsPct = savings > 0 ? Math.round((savings / side.product.originalPrice) * 100) : 0
                return (
                  <div key={si} className="text-center">
                    <p className="text-[0.65rem] text-theme-dim uppercase tracking-widest mb-1">Current Best Price</p>
                    <p className="text-[1.25rem] font-bold" style={{ color: side.color }}>{formatPrice(side.product.bestPrice)}</p>
                    {savingsPct > 0 && (
                      <p className="text-[0.7rem] text-[#22c55e] mt-1">↓ {savingsPct}% below original</p>
                    )}
                  </div>
                )
              })}
            </div>
          </GlassCard>
        </motion.div>
      </div>

      {/* ═══════ 8. HONEST PROS & CONS ═══════ */}
      <div className="mb-16">
        <SectionHeader icon={BarChart3} title="HONEST PROS & CONS" subtitle="AI-curated — no sponsored fluff" index={15} />
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {[
            { product: product1, pc: data.prosAndCons.product1, isWinner: winnerIndex === 0 },
            { product: product2, pc: data.prosAndCons.product2, isWinner: winnerIndex === 1 },
          ].map((side, si) => (
            <motion.div
              key={si}
              custom={16 + si}
              variants={sectionVariants}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true }}
            >
              <GlassCard winner={side.isWinner}>
                <div className="flex items-center gap-3 mb-6">
                  <div className="w-8 h-8 bg-white rounded-lg p-1 border border-theme-border">
                    <img src={side.product.image} alt={side.product.name} className="w-full h-full object-contain mix-blend-multiply" />
                  </div>
                  <p className="text-[0.75rem] font-medium text-theme-text">{side.product.name.split('(')[0].trim()}</p>
                </div>

                <div className="mb-6">
                  <p className="text-[0.65rem] font-bold uppercase tracking-[0.2em] text-[#22c55e] mb-3">
                    <span className="inline-flex items-center gap-1.5"><ThumbsUp className="w-3 h-3" /> Strengths</span>
                  </p>
                  {side.pc.pros.map((pro: string, i: number) => (
                    <ProConItem key={i} text={pro} isPro delay={i * 0.08} />
                  ))}
                </div>

                <div>
                  <p className="text-[0.65rem] font-bold uppercase tracking-[0.2em] text-[#ef4444] mb-3">
                    <span className="inline-flex items-center gap-1.5"><ThumbsDown className="w-3 h-3" /> Weaknesses</span>
                  </p>
                  {side.pc.cons.map((con: string, i: number) => (
                    <ProConItem key={i} text={con} isPro={false} delay={i * 0.08} />
                  ))}
                </div>
              </GlassCard>
            </motion.div>
          ))}
        </div>
      </div>

      {/* ═══════ 9. TRANSPARENT SCORING BREAKDOWN ═══════ */}
      <div className="mb-16">
        <SectionHeader icon={Zap} title="TRANSPARENT SCORING" subtitle="How we calculate the overall score — no hidden algorithms" index={18} />
        <motion.div
          custom={19}
          variants={sectionVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
        >
          <GlassCard>
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 items-center">
              {/* Pie Chart - Score Weights */}
              <div className="h-64">
                <p className="text-[0.65rem] font-bold uppercase tracking-[0.2em] text-theme-muted mb-4 text-center">Score Weights</p>
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={scoringPieData}
                      cx="50%"
                      cy="50%"
                      innerRadius={50}
                      outerRadius={80}
                      paddingAngle={3}
                      dataKey="value"
                    >
                      {scoringPieData.map((_, i) => (
                        <Cell key={i} fill={PIE_COLORS[i]} stroke="transparent" />
                      ))}
                    </Pie>
                    <Legend
                      wrapperStyle={{ fontSize: '10px', fontWeight: 500 }}
                      formatter={(value) => <span style={{ color: '#999' }}>{value}</span>}
                    />
                  </PieChart>
                </ResponsiveContainer>
              </div>

              {/* Product 1 Breakdown */}
              <div>
                <p className="text-[0.7rem] font-bold uppercase tracking-[0.15em] text-theme-muted mb-5">{p1Name.slice(0, 22)}</p>
                <MetricBar label="Price Score" value={data.scoring.product1.priceScore} color={PIE_COLORS[0]} delay={0.1} />
                <MetricBar label="Rating Score" value={data.scoring.product1.ratingScore} color={PIE_COLORS[1]} delay={0.2} />
                <MetricBar label="Deal Score" value={data.scoring.product1.dealScoreValue} color={PIE_COLORS[2]} delay={0.3} />
                <MetricBar label="Reviews Score" value={data.scoring.product1.reviewsScore} color={PIE_COLORS[3]} delay={0.4} />
              </div>

              {/* Product 2 Breakdown */}
              <div>
                <p className="text-[0.7rem] font-bold uppercase tracking-[0.15em] text-theme-muted mb-5">{p2Name.slice(0, 22)}</p>
                <MetricBar label="Price Score" value={data.scoring.product2.priceScore} color={PIE_COLORS[0]} delay={0.1} />
                <MetricBar label="Rating Score" value={data.scoring.product2.ratingScore} color={PIE_COLORS[1]} delay={0.2} />
                <MetricBar label="Deal Score" value={data.scoring.product2.dealScoreValue} color={PIE_COLORS[2]} delay={0.3} />
                <MetricBar label="Reviews Score" value={data.scoring.product2.reviewsScore} color={PIE_COLORS[3]} delay={0.4} />
              </div>
            </div>
          </GlassCard>
        </motion.div>
      </div>

      {/* ═══════ 10. FINAL VERDICT & VISUAL WINNER ═══════ */}
      <motion.div
        custom={20}
        variants={sectionVariants}
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true }}
        className="mb-8"
      >
        <div className="relative rounded-3xl overflow-hidden">
          {/* Animated gradient border */}
          <div className="absolute inset-0 rounded-3xl p-px bg-gradient-to-br from-[#22c55e40] via-[#3b82f640] to-[#a855f740]">
            <div className="w-full h-full rounded-3xl bg-theme-bg" />
          </div>

          <div className="relative px-8 py-16 md:px-16 md:py-20">
            <div className="text-center max-w-2xl mx-auto">
              <motion.div
                initial={{ scale: 0, rotate: -180 }}
                whileInView={{ scale: 1, rotate: 0 }}
                viewport={{ once: true }}
                transition={{ type: 'spring', stiffness: 150, damping: 15, delay: 0.2 }}
                className="w-20 h-20 mx-auto mb-8 rounded-3xl bg-gradient-to-br from-[#22c55e] to-[#3b82f6] flex items-center justify-center shadow-[0_0_60px_rgba(34,197,94,0.3)]"
              >
                <Sparkles className="w-10 h-10 text-white" />
              </motion.div>

              <p className="text-[0.65rem] font-bold uppercase tracking-[0.3em] text-[#a855f7] mb-4">
                BRANDBATTLE AI — FINAL VERDICT
              </p>

              {winnerIndex !== null ? (
                <>
                  <h2 className="text-[2rem] md:text-[2.5rem] font-[var(--font-display)] font-medium tracking-tight text-theme-text mb-4">
                    We recommend <span className="text-[#22c55e]">{winnerName}</span>
                  </h2>
                  <p className="text-[0.9rem] text-theme-secondary leading-relaxed mb-8">
                    Based on our analysis of {Object.keys(data.realWorldPerformance.product1).length * 2} performance metrics,
                    community sentiment from 3 major platforms, price history, brand reliability, and user persona matching —
                    {' '}{winnerName} emerges as the smarter purchase for the majority of users.
                  </p>

                  <div className="flex flex-wrap items-center justify-center gap-3">
                    <span className="px-5 py-2 rounded-full bg-gradient-to-r from-[#22c55e20] to-[#3b82f620] border border-[#22c55e30] text-[0.65rem] font-bold uppercase tracking-widest text-[#22c55e]">
                      ✦ {data.verdict.primary}
                    </span>
                    <span className="px-5 py-2 rounded-full bg-[#a855f715] border border-[#a855f730] text-[0.65rem] font-bold uppercase tracking-widest text-[#a855f7]">
                      {data.verdict.confidence}% Confidence Score
                    </span>
                  </div>
                </>
              ) : (
                <>
                  <h2 className="text-[2rem] md:text-[2.5rem] font-[var(--font-display)] font-medium tracking-tight text-theme-text mb-4">
                    Too Close to Call
                  </h2>
                  <p className="text-[0.9rem] text-theme-secondary leading-relaxed mb-8">
                    Both products deliver exceptional value. Your choice should depend on which specific use-case matters most to you.
                    Review the persona scores and real-world metrics above to make your final decision.
                  </p>
                </>
              )}

              <div className="flex items-center justify-center gap-2 mt-8">
                <BadgeCheck className="w-4 h-4 text-[#22c55e]" />
                <span className="text-[0.65rem] text-theme-dim tracking-wider uppercase">
                  Powered by BrandBattle AI • Your AI-Powered Buying Intelligence Platform
                </span>
              </div>
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  )
}

'use client'

import { useState, useMemo, useEffect } from 'react'
import Link from 'next/link'
import { motion, AnimatePresence } from 'framer-motion'
import {
  ArrowLeft,
  ArrowUpRight,
  ShieldCheck,
  Zap,
  Battery,
  Cpu,
  Smartphone,
  HardDrive,
  Star,
  CheckCircle2,
  Sparkles,
  Share2,
  GitCompare,
  Clock,
  Check,
  Award,
  Flag,
} from 'lucide-react'
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'
import { PRODUCTS, PLATFORMS, generatePriceHistory, formatPrice } from '@/data/demoData'
import api from '@/lib/api'
import TrustDashboard from '@/components/product/TrustDashboard'

interface ProductDetailClientProps {
  initialId: string
}

export default function ProductDetailClient({ initialId }: ProductDetailClientProps) {
  const id = initialId
  const demoProduct = PRODUCTS.find(p => p.id === parseInt(id)) || PRODUCTS[0]

  const [apiProduct, setApiProduct] = useState<any>(null)
  const [apiPrices, setApiPrices] = useState<any[] | null>(null)

  useEffect(() => {
    let isMounted = true
    const fetchRealData = async () => {
      try {
        const prodRes = await api.products.getById(parseInt(id))
        if (prodRes.data && isMounted) {
          setApiProduct(prodRes.data)
        }
      } catch {
        // Fallback to demo data
      }
      try {
        const pricesRes = await api.products.getPrices(parseInt(id))
        if (pricesRes.data && isMounted) {
          setApiPrices(pricesRes.data)
        }
      } catch {
        // Fallback
      }
    }
    fetchRealData()
    return () => { isMounted = false }
  }, [id])

  const product = useMemo(() => {
    if (!apiProduct) return demoProduct
    return {
      ...demoProduct,
      name: apiProduct.name || demoProduct.name,
      bestPrice: apiProduct.current_best_price || demoProduct.bestPrice,
      originalPrice: apiProduct.highest_price || demoProduct.originalPrice,
      bestPlatform: apiProduct.current_best_platform || demoProduct.bestPlatform,
      rating: apiProduct.average_rating || demoProduct.rating,
      totalReviews: apiProduct.total_reviews || demoProduct.totalReviews,
      image: apiProduct.image_url || demoProduct.image,
      price_verified_at: apiProduct.price_verified_at,
      price_verification_status: apiProduct.price_verification_status,
    }
  }, [apiProduct, demoProduct])

  const priceHistory = useMemo(() => generatePriceHistory(product.bestPrice), [product])

  const suggestedProduct = useMemo(() => {
    const currentCat = (product.category || '').toLowerCase().trim()
    const similarProducts = PRODUCTS.filter(p => p.id !== product.id && (p.category || '').toLowerCase().trim() === currentCat)
    similarProducts.sort((a, b) => Math.abs(a.bestPrice - product.bestPrice) - Math.abs(b.bestPrice - product.bestPrice))
    return similarProducts[0] || PRODUCTS.find(p => p.id !== product.id && (p.category || '').toLowerCase().trim() === currentCat) || product
  }, [product])

  const recommendedAlternatives = useMemo(() => {
    const currentCat = (product.category || '').toLowerCase().trim()
    let matches = PRODUCTS.filter(p => p.id !== product.id && (p.category || '').toLowerCase().trim() === currentCat)
    if (matches.length === 0) {
      matches = PRODUCTS.filter(p => {
        if (p.id === product.id) return false
        const candCat = (p.category || '').toLowerCase().trim()
        return candCat.includes(currentCat) || currentCat.includes(candCat)
      })
    }
    return matches.length > 0 ? matches.slice(0, 3) : [suggestedProduct]
  }, [product, suggestedProduct])

  // Gallery state
  const [selectedImage, setSelectedImage] = useState(product.image)
  useEffect(() => {
    setSelectedImage(product.image)
  }, [product.id, product.image])

  // Tab navigation state
  const [activeTab, setActiveTab] = useState<'overview' | 'specs' | 'providers' | 'history' | 'similar'>('overview')

  // Wishlist / Share state
  const [isCopied, setIsCopied] = useState(false)

  // Price Tracking Radar Modal State
  const [showTrackModal, setShowTrackModal] = useState(false)
  const [targetPrice, setTargetPrice] = useState(Math.round(product.bestPrice * 0.9))
  const [trackedPlatforms, setTrackedPlatforms] = useState(product.prices.map(p => p.platform))
  const [isAlertSubmitting, setIsAlertSubmitting] = useState(false)
  const [alertSuccess, setAlertSuccess] = useState(false)
  const [alertEmail, setAlertEmail] = useState('')
  const [isReportSubmitted, setIsReportSubmitted] = useState(false)

  useEffect(() => {
    setTargetPrice(Math.round(product.bestPrice * 0.9))
    setTrackedPlatforms(product.prices.map(p => p.platform))
    setAlertSuccess(false)
  }, [product.id, product.bestPrice, product.prices])

  // Generate gallery thumbnails
  const thumbnails = useMemo(() => {
    return [
      product.image,
      product.image, // Alternative view placeholder
      product.image, // Detail view placeholder
    ]
  }, [product.image])

  // Spec highlights map
  const highlightCards = [
    {
      icon: Battery,
      title: 'Battery',
      value: (product.specs as any)['Battery'] || '5000mAh',
      label: 'All-Day High Endurance Power'
    },
    {
      icon: Smartphone,
      title: 'Display',
      value: (product.specs as any)['Display'] || '6.67" AMOLED',
      label: '120Hz Smooth Refresh Rate'
    },
    {
      icon: Cpu,
      title: 'Processor',
      value: (product.specs as any)['Processor'] || 'Performance Chipset',
      label: 'AI-Optimized Performance'
    },
    {
      icon: HardDrive,
      title: 'Storage',
      value: (product.specs as any)['Storage'] || (product.specs as any)['RAM'] || '256GB High-Speed',
      label: 'Ultra-Fast Flash Storage'
    }
  ]

  const discountPercent = Math.round(((product.originalPrice - product.bestPrice) / product.originalPrice) * 100)
  const totalSavings = product.originalPrice - product.bestPrice

  const handleShare = () => {
    if (navigator.clipboard) {
      navigator.clipboard.writeText(window.location.href)
      setIsCopied(true)
      setTimeout(() => setIsCopied(false), 2000)
    }
  }

  const scrollToSection = (sectionId: string, tabName: typeof activeTab) => {
    setActiveTab(tabName)
    const element = document.getElementById(sectionId)
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'start' })
    }
  }

  return (
    <div className="min-h-screen bg-[#050505] text-[#ffffff] pt-32 pb-48 selection:bg-[#f20ab0] selection:text-white">
      {/* ─── BREADCRUMB & BACK NAVIGATION ─── */}
      <div className="w-full max-w-[1600px] mx-auto px-6 md:px-12 lg:px-20 mb-12">
        <Link
          href="/search"
          className="inline-flex items-center gap-3 text-[0.75rem] font-medium uppercase tracking-[0.2em] text-[#71717a] hover:text-[#f20ab0] transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Catalog</span>
        </Link>
      </div>

      {/* ─── MAIN 12-COLUMN EDITORIAL HERO SECTION ─── */}
      <div className="w-full max-w-[1600px] mx-auto px-6 md:px-12 lg:px-20 mb-32">
        <div className="grid grid-cols-12 gap-8 lg:gap-16 items-start">
          
          {/* ─── GALLERY (45% Width / 5 Columns on lg) ─── */}
          <div className="col-span-12 lg:col-span-5 relative lg:sticky lg:top-36">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, ease: [0.22, 1, 0.36, 1] }}
              className="relative aspect-square bg-[#0c0c0e] border border-[#1a1a20] rounded-3xl p-6 sm:p-12 md:p-16 flex items-center justify-center overflow-hidden group shadow-[0_20px_60px_rgba(0,0,0,0.8)]"
            >
              {/* Subtle ambient lighting */}
              <div className="absolute -top-24 -left-24 w-64 h-64 bg-[#f20ab0]/10 blur-[100px] rounded-full pointer-events-none" />
              <div className="absolute -bottom-24 -right-24 w-64 h-64 bg-[#ffffff]/5 blur-[100px] rounded-full pointer-events-none" />

              {/* Deal Badge Overlay */}
              {discountPercent > 0 && (
                <div className="absolute top-4 left-4 sm:top-6 sm:left-6 z-10 px-3 sm:px-4 py-1.5 sm:py-2 bg-[#f20ab0] text-white text-[0.65rem] sm:text-[0.7rem] font-bold uppercase tracking-[0.2em] rounded-full shadow-[0_0_20px_rgba(242,10,176,0.5)]">
                  -{discountPercent}% OFF
                </div>
              )}

              {/* Main Image */}
              <motion.img
                key={selectedImage}
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
                src={selectedImage}
                alt={product.name}
                className="max-w-full max-h-full object-contain filter drop-shadow-[0_25px_35px_rgba(0,0,0,0.9)] group-hover:scale-105 transition-transform duration-700 ease-out"
              />
            </motion.div>

            {/* Thumbnail Strip */}
            <div className="flex gap-3 sm:gap-4 mt-4 sm:mt-6 justify-center">
              {thumbnails.map((thumb, idx) => {
                const isActive = selectedImage === thumb
                return (
                  <button
                    key={idx}
                    onClick={() => setSelectedImage(thumb)}
                    className={`relative w-16 h-16 sm:w-20 sm:h-20 bg-[#0c0c0e] border rounded-2xl p-2 sm:p-3 flex items-center justify-center overflow-hidden transition-all duration-300 ${
                      isActive
                        ? 'border-[#f20ab0] shadow-[0_0_15px_rgba(242,10,176,0.3)] scale-105'
                        : 'border-[#1a1a20] opacity-60 hover:opacity-100 hover:border-[#3f3f46]'
                    }`}
                  >
                    <img src={thumb} alt={`${product.name} view ${idx + 1}`} className="max-w-full max-h-full object-contain" />
                  </button>
                )
              })}
            </div>
          </div>

          {/* ─── PRODUCT INFORMATION (55% Width / 7 Columns on lg) ─── */}
          <div className="col-span-12 lg:col-span-7 space-y-6 sm:space-y-10 mt-6 lg:mt-0">
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.1, ease: [0.22, 1, 0.36, 1] }}
            >
              {/* Brand & Category Header */}
              <div className="flex items-center gap-4 mb-4">
                <span className="text-[0.9rem] font-semibold uppercase tracking-[0.25em] text-[#a1a1aa]">
                  {product.brand}
                </span>
                <span className="text-[#3f3f46]">·</span>
                <span className="text-[0.8rem] font-medium uppercase tracking-[0.18em] text-[#71717a]">
                  {product.category}
                </span>
              </div>

              {/* Product Name (52-64px Editorial Headline) */}
              <h1 className="text-[2.75rem] sm:text-[3.5rem] lg:text-[4rem] font-bold font-[var(--font-display)] text-white tracking-tight leading-[1.02] mb-3">
                {product.name}
              </h1>

              {/* Variant Tag */}
              <div className="text-[1.25rem] font-medium text-[#f20ab0] tracking-wide mb-6">
                {(product.specs as any)['Storage'] || (product.specs as any)['RAM'] || '256GB High-Speed Edition'}
              </div>

              {/* Short AI Summary */}
              <p className="text-[1.125rem] text-[#a1a1aa] leading-[1.65] max-w-2xl font-light mb-8">
                {product.description}
              </p>

              {/* Ratings & Authenticated Badges */}
              <div className="flex flex-wrap items-center gap-6 pb-8 border-b border-[#1a1a20]">
                <div className="flex items-center gap-2 bg-[#0c0c0e] px-4 py-2 rounded-full border border-[#1a1a20]">
                  <Star className="w-4 h-4 text-[#f20ab0] fill-[#f20ab0]" />
                  <span className="text-[0.875rem] font-bold text-white">{product.rating}</span>
                  <span className="text-[0.75rem] text-[#71717a]">({(product as any).reviewsCount || (product as any).totalReviews || 128} Reviews)</span>
                </div>

                <div className="flex items-center gap-2 bg-[#0c0c0e] px-4 py-2 rounded-full border border-[#1a1a20]">
                  <Award className="w-4 h-4 text-[#22c55e]" />
                  <span className="text-[0.75rem] font-semibold uppercase tracking-wider text-[#22c55e]">
                    Deal Score: {product.dealScore}/100
                  </span>
                </div>

                <div className="flex items-center gap-2 text-[0.75rem] text-[#71717a] font-medium uppercase tracking-wider">
                  <ShieldCheck className="w-4 h-4 text-[#a1a1aa]" />
                  Verified Authentic
                </div>
              </div>
            </motion.div>

            {/* ─── 4. TRUST & AUTHENTICITY RADAR (ALWAYS VISIBLE) ─── */}
            <TrustDashboard
              productId={product.id}
              productName={product.name}
              brand={product.brand}
              bestPrice={product.bestPrice}
              originalPrice={product.originalPrice}
              bestPlatform={product.bestPlatform}
              priceVerifiedAt={(product as any).price_verified_at}
              prices={apiPrices || undefined}
            />

            {/* ─── PREMIUM PRICING CARD ─── */}
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.2, ease: [0.22, 1, 0.36, 1] }}
              className="bg-[#0c0c0e] border border-[#1a1a20] rounded-3xl p-8 lg:p-10 space-y-8 relative overflow-hidden shadow-[0_15px_40px_rgba(0,0,0,0.5)]"
            >
              {/* Subtle card glow */}
              <div className="absolute top-0 right-0 w-48 h-48 bg-[#f20ab0]/5 blur-3xl pointer-events-none" />

              <div className="flex flex-wrap items-baseline justify-between gap-4">
                <div>
                  <span className="text-[0.7rem] font-mono uppercase tracking-[0.2em] text-[#71717a] block mb-2">
                    Lowest Price Today
                  </span>
                  <div className="flex items-baseline gap-4">
                    <span className="text-[3rem] lg:text-[3.5rem] font-bold font-[var(--font-display)] text-white leading-none">
                      {formatPrice(product.bestPrice)}
                    </span>
                    <span className="text-[1.25rem] text-[#71717a] line-through font-light">
                      {formatPrice(product.originalPrice)}
                    </span>
                  </div>
                </div>

                {totalSavings > 0 && (
                  <div className="text-right">
                    <span className="inline-block px-4 py-2 bg-[#f20ab0]/10 border border-[#f20ab0]/30 text-[#f20ab0] text-[0.8rem] font-bold uppercase tracking-widest rounded-xl">
                      Save {formatPrice(totalSavings)}
                    </span>
                  </div>
                )}
              </div>

              {/* Best Marketplace & Stock Info */}
              <div className="grid grid-cols-2 gap-4 py-4 border-y border-[#1a1a20] text-[0.85rem]">
                <div>
                  <span className="text-[#71717a] block text-[0.7rem] uppercase tracking-wider mb-1">Best Marketplace</span>
                  <span className="font-semibold text-white flex items-center gap-2">
                    {(PLATFORMS as any)[product.bestPlatform]?.name || 'Amazon'}
                    <CheckCircle2 className="w-3.5 h-3.5 text-[#22c55e]" />
                  </span>
                </div>
                <div>
                  <span className="text-[#71717a] block text-[0.7rem] uppercase tracking-wider mb-1">Availability</span>
                  <span className="font-semibold text-[#22c55e] flex items-center gap-2">
                    In Stock · Ships Free
                  </span>
                </div>
              </div>

              {/* ─── ACTION BUTTONS (CTAs) ─── */}
              <div className="space-y-4">
                <button
                  type="button"
                  onClick={() => setShowTrackModal(true)}
                  className="w-full py-5 bg-[#f20ab0] text-white text-[0.875rem] font-bold uppercase tracking-[0.2em] rounded-2xl hover:bg-[#d00896] transition-all duration-300 shadow-[0_0_30px_rgba(242,10,176,0.4)] hover:shadow-[0_0_40px_rgba(242,10,176,0.6)] hover:scale-[1.01] active:scale-[0.99] flex items-center justify-center gap-3"
                >
                  <Zap className="w-4 h-4 fill-white" />
                  View Prices & Offers ({product.prices.length} Stores)
                </button>

                <div className="grid grid-cols-3 gap-3">
                  <Link
                    href={`/compare?p1=${product.id}&p2=${suggestedProduct.id}`}
                    className="py-4 bg-[#141418] border border-[#27272a] hover:border-[#f20ab0] text-white text-[0.75rem] font-medium uppercase tracking-wider rounded-xl transition-all duration-300 flex items-center justify-center gap-2 hover:bg-[#1a1a20]"
                  >
                    <GitCompare className="w-4 h-4 text-[#a1a1aa]" />
                    Compare
                  </Link>

                  <button
                    type="button"
                    onClick={() => setShowTrackModal(true)}
                    className="py-4 bg-[#141418] border border-[#27272a] hover:border-[#f20ab0] text-white text-[0.75rem] font-medium uppercase tracking-wider rounded-xl transition-all duration-300 flex items-center justify-center gap-2 hover:bg-[#1a1a20]"
                  >
                    <Clock className="w-4 h-4 text-[#a1a1aa]" />
                    Track Price
                  </button>

                  <button
                    type="button"
                    onClick={handleShare}
                    className="py-4 bg-[#141418] border border-[#27272a] hover:border-[#f20ab0] text-white text-[0.75rem] font-medium uppercase tracking-wider rounded-xl transition-all duration-300 flex items-center justify-center gap-2 hover:bg-[#1a1a20]"
                  >
                    <Share2 className="w-4 h-4 text-[#a1a1aa]" />
                    {isCopied ? 'Copied!' : 'Share'}
                  </button>
                </div>
              </div>
            </motion.div>

            {/* ─── HIGHLIGHT SPECIFICATION CARDS GRID ─── */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 pt-4">
              {highlightCards.map((card, i) => (
                <div
                  key={i}
                  className="bg-[#0c0c0e] border border-[#1a1a20] rounded-2xl p-5 hover:border-[#f20ab0]/50 transition-all duration-300 group"
                >
                  <card.icon className="w-5 h-5 text-[#f20ab0] mb-3 group-hover:scale-110 transition-transform" />
                  <span className="text-[0.65rem] font-semibold uppercase tracking-widest text-[#71717a] block mb-1">
                    {card.title}
                  </span>
                  <div className="text-[0.95rem] font-bold text-white mb-1 truncate">{card.value}</div>
                  <div className="text-[0.65rem] text-[#a1a1aa] font-light leading-tight">{card.label}</div>
                </div>
              ))}
            </div>

            {/* Report Incorrect Information Feedback Button */}
            <div className="pt-4 flex justify-end">
              {isReportSubmitted ? (
                <span className="inline-flex items-center gap-1.5 text-xs text-[#22c55e] font-medium">
                  <Check className="w-3.5 h-3.5" /> Thank you! Report submitted to moderation queue.
                </span>
              ) : (
                <button
                  onClick={() => setIsReportSubmitted(true)}
                  className="inline-flex items-center gap-2 text-xs text-[#71717a] hover:text-[#f20ab0] transition-colors font-medium"
                >
                  <Flag className="w-3.5 h-3.5" /> Found incorrect information? Help us improve.
                </button>
              )}
            </div>

          </div>
        </div>
      </div>

      {/* ─── STICKY TAB NAVIGATION BAR ─── */}
      <div className="sticky top-20 z-40 bg-[#050505]/90 backdrop-blur-xl border-y border-[#1a1a20] mb-24">
        <div className="w-full max-w-[1600px] mx-auto px-6 md:px-12 lg:px-20 flex overflow-x-auto hide-scrollbar gap-8 lg:gap-12 py-5 text-[0.8rem] font-medium uppercase tracking-[0.18em]">
          {[
            { id: 'overview', label: 'Overview', section: 'section-overview' },
            { id: 'specs', label: 'Specifications', section: 'section-specs' },
            { id: 'providers', label: 'Market Prices', section: 'section-providers' },
            { id: 'history', label: 'Price History', section: 'section-history' },
            { id: 'similar', label: 'Similar Products', section: 'section-similar' },
          ].map(tab => {
            const isActive = activeTab === tab.id
            return (
              <button
                key={tab.id}
                onClick={() => scrollToSection(tab.section, tab.id as any)}
                className={`relative shrink-0 transition-colors duration-300 pb-1 ${
                  isActive ? 'text-white font-bold' : 'text-[#71717a] hover:text-white'
                }`}
              >
                {tab.label}
                {isActive && (
                  <motion.div
                    layoutId="activeTabIndicator"
                    className="absolute bottom-0 left-0 right-0 h-[2px] bg-[#f20ab0]"
                    transition={{ type: 'spring', stiffness: 400, damping: 30 }}
                  />
                )}
              </button>
            )
          })}
        </div>
      </div>

      {/* ─── CONTENT SECTIONS CONTAINER ─── */}
      <div className="w-full max-w-[1600px] mx-auto px-6 md:px-12 lg:px-20 space-y-32">

        {/* SECTION 1: OVERVIEW & HARDWARE SPECIFICATIONS */}
        <section id="section-overview" className="scroll-mt-36">
          <div className="mb-12">
            <span className="text-[0.75rem] font-medium uppercase tracking-[0.2em] text-[#f20ab0] block mb-2">
              Engineering Specs
            </span>
            <h2 className="text-[2.25rem] lg:text-[3rem] font-bold font-[var(--font-display)] text-white tracking-tight">
              Hardware Overview.
            </h2>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-12 gap-12">
            {/* Left: Spec Table */}
            <div className="lg:col-span-7 bg-[#0c0c0e] border border-[#1a1a20] rounded-3xl p-8 lg:p-12">
              <ul className="divide-y divide-[#1a1a20]">
                {Object.entries(product.specs).map(([key, value]) => (
                  <li key={key} className="py-5 flex justify-between items-center text-[0.95rem]">
                    <span className="text-[0.75rem] font-semibold uppercase tracking-[0.15em] text-[#71717a]">
                      {key}
                    </span>
                    <span className="font-medium text-white text-right">{String(value)}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Right: AI Intelligence Card */}
            <div className="lg:col-span-5 bg-[#0c0c0e] border border-[#1a1a20] rounded-3xl p-8 lg:p-12 flex flex-col justify-between relative overflow-hidden">
              <div className="absolute top-0 right-0 w-64 h-64 bg-[#f20ab0]/10 blur-3xl pointer-events-none" />
              <div>
                <div className="flex items-center gap-3 mb-6 text-[#f20ab0]">
                  <Sparkles className="w-5 h-5" />
                  <span className="text-[0.75rem] font-bold uppercase tracking-[0.2em]">
                    Brand Battle Intelligence Summary
                  </span>
                </div>
                <h3 className="text-[1.5rem] font-bold text-white mb-6 leading-snug">
                  Precision Hardware Evaluation & Value Analysis
                </h3>
                <p className="text-[#a1a1aa] leading-relaxed text-[0.95rem] font-light mb-8">
                  Our Knowledge Graph cross-analyzed {product.name} against {PRODUCTS.length} competing models in the {product.category} class. It maintains a top-tier deal confidence score of {product.dealScore}/100.
                </p>
              </div>

              <div className="p-6 bg-[#141418] border border-[#27272a] rounded-2xl space-y-3">
                <div className="flex justify-between items-center text-[0.8rem]">
                  <span className="text-[#71717a] uppercase tracking-wider">Hardware Score</span>
                  <span className="font-bold text-[#22c55e]">9.4 / 10</span>
                </div>
                <div className="w-full h-1.5 bg-[#27272a] rounded-full overflow-hidden">
                  <div className="w-[94%] h-full bg-[#22c55e] rounded-full" />
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* SECTION 2: MARKET PROVIDERS & PRICE COMPARISON */}
        <section id="section-providers" className="scroll-mt-36">
          <div className="mb-12">
            <span className="text-[0.75rem] font-medium uppercase tracking-[0.2em] text-[#f20ab0] block mb-2">
              Cross-Platform Audit
            </span>
            <h2 className="text-[2.25rem] lg:text-[3rem] font-bold font-[var(--font-display)] text-white tracking-tight">
              Marketplace Offers.
            </h2>
          </div>

          <div className="bg-[#0c0c0e] border border-[#1a1a20] rounded-3xl p-8 lg:p-12">
            <div className="divide-y divide-[#1a1a20]">
              {product.prices.sort((a, b) => a.price - b.price).map((p, i) => {
                const isBest = i === 0
                const premiumPct = Math.round(((p.price - product.bestPrice) / product.bestPrice) * 100)
                return (
                  <a
                    key={p.platform}
                    href="#"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="py-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4 group hover:px-4 transition-all duration-300 rounded-2xl"
                  >
                    <div className="flex items-center gap-6">
                      <span className="text-[0.75rem] font-mono text-[#71717a] w-6">0{i + 1}</span>
                      <span className="text-[1.25rem] font-semibold text-white group-hover:text-[#f20ab0] transition-colors">
                        {(PLATFORMS as any)[p.platform]?.name || p.platform}
                      </span>
                      {isBest && (
                        <span className="px-3 py-1 bg-[#22c55e]/10 border border-[#22c55e]/30 text-[#22c55e] text-[0.65rem] font-bold uppercase tracking-widest rounded-full">
                          Lowest Price
                        </span>
                      )}
                    </div>

                    <div className="flex items-center gap-8 justify-between sm:justify-end">
                      <div className="text-right">
                        <span className="text-[1.375rem] font-bold text-white block">
                          {formatPrice(p.price)}
                        </span>
                        {!isBest && (
                          <span className="text-[0.7rem] text-[#71717a]">+{premiumPct}% higher</span>
                        )}
                      </div>
                      <ArrowUpRight className="w-5 h-5 text-[#71717a] group-hover:text-[#f20ab0] group-hover:translate-x-1 group-hover:-translate-y-1 transition-all duration-300" />
                    </div>
                  </a>
                )
              })}
            </div>
          </div>
        </section>

        {/* SECTION 3: 90-DAY PRICE TREND ANALYSIS */}
        <section id="section-history" className="scroll-mt-36">
          <div className="mb-12 flex flex-col md:flex-row md:items-end justify-between gap-6">
            <div>
              <span className="text-[0.75rem] font-medium uppercase tracking-[0.2em] text-[#f20ab0] block mb-2">
                Historical Intelligence
              </span>
              <h2 className="text-[2.25rem] lg:text-[3rem] font-bold font-[var(--font-display)] text-white tracking-tight">
                90-Day Price Trend Analysis.
              </h2>
            </div>
            <div className="flex items-center gap-6 text-[0.75rem] font-mono text-[#a1a1aa]">
              <div className="flex items-center gap-2">
                <span className="w-3 h-3 bg-[#f20ab0] rounded-full inline-block" />
                Amazon Price
              </div>
              <div className="flex items-center gap-2">
                <span className="w-3 h-3 bg-[#71717a] rounded-full inline-block" />
                Flipkart Price
              </div>
            </div>
          </div>

          <div className="bg-[#0c0c0e] border border-[#1a1a20] rounded-3xl p-6 lg:p-10 h-[450px]">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={priceHistory.filter((_, i) => i % 4 === 0)}>
                <defs>
                  <linearGradient id="gradientAmazon" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#f20ab0" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#f20ab0" stopOpacity={0.0} />
                  </linearGradient>
                </defs>
                <XAxis
                  dataKey="date"
                  tickLine={false}
                  axisLine={false}
                  tick={{ fontSize: 11, fill: '#71717a' }}
                  tickFormatter={v => v.slice(5)}
                  dy={10}
                />
                <YAxis
                  tickLine={false}
                  axisLine={false}
                  tick={{ fontSize: 11, fill: '#71717a' }}
                  domain={['dataMin - 50', 'dataMax + 50']}
                  dx={-10}
                />
                <Tooltip
                  contentStyle={{
                    background: '#050505',
                    border: '1px solid #27272a',
                    borderRadius: '12px',
                    fontSize: '12px',
                    color: '#fff'
                  }}
                />
                <Area type="monotone" dataKey="amazon" stroke="#f20ab0" strokeWidth={3} fill="url(#gradientAmazon)" />
                <Area type="monotone" dataKey="flipkart" stroke="#71717a" strokeWidth={2} fill="transparent" strokeDasharray="4 4" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </section>

        {/* SECTION 4: SIMILAR PRODUCTS / RECOMMENDED ALTERNATIVES */}
        <section id="section-similar" className="scroll-mt-36">
          <div className="mb-12 flex justify-between items-end">
            <div>
              <span className="text-[0.75rem] font-medium uppercase tracking-[0.2em] text-[#f20ab0] block mb-2">
                Competitive Analysis
              </span>
              <h2 className="text-[2.25rem] lg:text-[3rem] font-bold font-[var(--font-display)] text-white tracking-tight">
                Recommended Alternatives.
              </h2>
            </div>
            <Link href="/search" className="text-[0.8rem] font-semibold uppercase tracking-[0.15em] text-[#f20ab0] hover:text-white transition-colors">
              View Catalog →
            </Link>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {recommendedAlternatives.map(sim => (
              <Link
                key={sim.id}
                href={`/product/${sim.id}`}
                className="bg-[#0c0c0e] border border-[#1a1a20] rounded-3xl p-8 hover:border-[#f20ab0]/50 transition-all duration-500 group flex flex-col justify-between"
              >
                <div>
                  <div className="aspect-square bg-[#050505] rounded-2xl p-8 mb-6 flex items-center justify-center overflow-hidden">
                    <img src={sim.image} alt={sim.name} className="max-h-full object-contain group-hover:scale-105 transition-transform duration-500" />
                  </div>
                  <span className="text-[0.7rem] font-semibold uppercase tracking-widest text-[#71717a] block mb-2">
                    {sim.brand}
                  </span>
                  <h4 className="text-[1.25rem] font-bold text-white mb-2 group-hover:text-[#f20ab0] transition-colors">
                    {sim.name}
                  </h4>
                </div>
                <div className="flex justify-between items-baseline pt-6 border-t border-[#1a1a20] mt-6">
                  <span className="text-[1.25rem] font-bold text-white">{formatPrice(sim.bestPrice)}</span>
                  <span className="text-[0.75rem] text-[#f20ab0] font-semibold uppercase tracking-wider">
                    Compare Specs →
                  </span>
                </div>
              </Link>
            ))}
          </div>
        </section>

      </div>

      {/* ─── PRESERVED PRICE TRACKING RADAR MODAL ─── */}
      <AnimatePresence>
        {showTrackModal && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-6">
            {/* Backdrop */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setShowTrackModal(false)}
              className="absolute inset-0 bg-black/85 backdrop-blur-md"
            />

            {/* Modal Container */}
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 20 }}
              transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
              className="relative bg-[#09090b] border border-[#27272a] rounded-3xl p-8 max-w-lg w-full z-10 shadow-[0_25px_60px_rgba(0,0,0,0.9)] overflow-hidden"
            >
              {/* Visual Ambient Highlights */}
              <div className="absolute -top-32 -right-32 w-64 h-64 bg-[#f20ab0] opacity-10 blur-3xl rounded-full pointer-events-none" />
              <div className="absolute -bottom-32 -left-32 w-64 h-64 bg-[#22c55e] opacity-10 blur-3xl rounded-full pointer-events-none" />

              {alertSuccess ? (
                <motion.div
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="py-12 flex flex-col items-center text-center"
                >
                  <div className="w-20 h-20 bg-[#22c55e]/10 border border-[#22c55e]/30 rounded-full flex items-center justify-center mb-8">
                    <motion.span
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      transition={{ delay: 0.2, type: 'spring', stiffness: 200 }}
                      className="text-4xl text-[#22c55e]"
                    >
                      ✓
                    </motion.span>
                  </div>
                  <h2 className="text-[2rem] font-[var(--font-display)] font-medium leading-[1.2] text-white mb-4 uppercase tracking-wider">
                    ALERT ACTIVATED.
                  </h2>
                  <p className="text-[#a1a1aa] text-[0.875rem] leading-relaxed max-w-xs mb-8">
                    Our price tracking engine will monitor this product 24/7 across selected platforms and notify you instantly.
                  </p>
                  <div className="px-5 py-2 bg-[#141418] rounded-full border border-[#27272a] text-[0.75rem] font-mono text-[#a1a1aa] uppercase tracking-widest">
                    Target: {formatPrice(targetPrice)}
                  </div>
                </motion.div>
              ) : (
                <>
                  {/* Header */}
                  <div className="flex justify-between items-start mb-8">
                    <div>
                      <span className="text-[0.65rem] font-mono font-medium uppercase tracking-[0.2em] text-[#f20ab0] block mb-2">
                        Automated Radar
                      </span>
                      <h2 className="text-[2rem] font-[var(--font-display)] font-bold text-white uppercase tracking-tight">
                        Track Price.
                      </h2>
                    </div>
                    <button
                      onClick={() => setShowTrackModal(false)}
                      className="w-10 h-10 rounded-full border border-[#27272a] flex items-center justify-center hover:bg-[#141418] transition-colors text-[#71717a] hover:text-white"
                    >
                      ✕
                    </button>
                  </div>

                  {/* Product Summary */}
                  <div className="flex items-center gap-4 bg-[#141418] border border-[#27272a] rounded-2xl p-4 mb-6">
                    <div className="w-16 h-16 bg-[#050505] p-2 rounded-xl flex items-center justify-center shrink-0">
                      <img src={product.image} className="max-w-full max-h-full object-contain" alt={product.name} />
                    </div>
                    <div className="min-w-0 flex-1">
                      <p className="text-[0.65rem] font-bold uppercase tracking-widest text-[#71717a] mb-0.5">{product.brand}</p>
                      <h4 className="font-medium text-white text-[0.875rem] truncate">{product.name}</h4>
                      <p className="text-[0.75rem] font-medium text-[#a1a1aa] mt-1">Current best: {formatPrice(product.bestPrice)}</p>
                    </div>
                  </div>

                  {/* AI Diagnostic Alert */}
                  <div className="mb-6 bg-[#141418]/60 border border-[#27272a] rounded-xl p-4 flex gap-3">
                    <span className="text-[1.25rem]">{product.dealScore >= 85 ? '🟢' : '🟡'}</span>
                    <div>
                      <span className="text-[0.65rem] font-bold uppercase tracking-widest text-white block mb-1">
                        {product.dealScore >= 85 ? 'Buy Signal Active' : 'Hold Signal / High Tracker Recommendation'}
                      </span>
                      <p className="text-[0.75rem] text-[#a1a1aa] leading-relaxed">
                        {product.dealScore >= 85
                          ? `This item has a premium deal score of ${product.dealScore}/100. Price is near historical low.`
                          : 'This product is currently at standard pricing. Setting a price alert is highly advised.'}
                      </p>
                    </div>
                  </div>

                  {/* Slider Target */}
                  <div className="mb-8">
                    <div className="flex justify-between items-baseline mb-3">
                      <label className="text-[0.7rem] font-mono font-medium uppercase tracking-[0.15em] text-[#a1a1aa]">Target Price</label>
                      <span className="text-[1.125rem] font-bold font-mono text-[#22c55e]">
                        {formatPrice(targetPrice)}
                        <span className="text-[0.75rem] text-[#71717a] font-normal ml-2">
                          ({Math.round(((product.bestPrice - targetPrice) / product.bestPrice) * 100)}% Drop)
                        </span>
                      </span>
                    </div>

                    <input
                      type="range"
                      min={Math.round(product.bestPrice * 0.5)}
                      max={product.bestPrice}
                      step="1"
                      value={targetPrice}
                      onChange={e => setTargetPrice(parseInt(e.target.value))}
                      className="w-full h-1 bg-[#27272a] rounded-lg appearance-none cursor-pointer accent-[#f20ab0]"
                    />

                    {/* Quick Preset Buttons */}
                    <div className="flex gap-2 mt-4">
                      {[0.9, 0.8, 0.7].map((pct, i) => {
                        const pctLabel = [10, 20, 30][i]
                        const presetVal = Math.round(product.bestPrice * pct)
                        return (
                          <button
                            key={pct}
                            type="button"
                            onClick={() => setTargetPrice(presetVal)}
                            className={`flex-1 py-2 text-[0.65rem] font-mono font-medium uppercase tracking-widest border transition-all duration-300 rounded-lg ${
                              targetPrice === presetVal
                                ? 'bg-[#f20ab0]/10 border-[#f20ab0] text-[#f20ab0]'
                                : 'bg-transparent text-[#71717a] border-[#27272a] hover:border-white hover:text-white'
                            }`}
                          >
                            -{pctLabel}% Preset
                          </button>
                        )
                      })}
                    </div>
                  </div>

                  {/* Platform Selectors */}
                  <div className="mb-8">
                    <label className="text-[0.7rem] font-mono font-medium uppercase tracking-[0.15em] text-[#a1a1aa] block mb-3">Monitor Stores</label>
                    <div className="flex flex-wrap gap-2.5">
                      {product.prices.map(p => {
                        const isSel = trackedPlatforms.includes(p.platform)
                        return (
                          <button
                            key={p.platform}
                            type="button"
                            onClick={() => {
                              if (isSel) {
                                if (trackedPlatforms.length > 1) {
                                  setTrackedPlatforms(trackedPlatforms.filter(pl => pl !== p.platform))
                                }
                              } else {
                                setTrackedPlatforms([...trackedPlatforms, p.platform])
                              }
                            }}
                            className={`px-4 py-2 flex items-center gap-2 border text-[0.7rem] font-mono font-medium uppercase tracking-widest rounded-full transition-all duration-300 ${
                              isSel
                                ? 'bg-[#f20ab0] text-white border-[#f20ab0] font-semibold'
                                : 'bg-transparent text-[#71717a] border-[#27272a] hover:border-white'
                            }`}
                          >
                            <span>{(PLATFORMS as Record<string, { icon: string; name: string }>)[p.platform]?.icon}</span>
                            <span>{(PLATFORMS as Record<string, { icon: string; name: string }>)[p.platform]?.name}</span>
                          </button>
                        )
                      })}
                    </div>
                  </div>

                  {/* Email Capture & Submit */}
                  <form
                    onSubmit={async e => {
                      e.preventDefault()
                      if (!alertEmail.trim()) return
                      setIsAlertSubmitting(true)
                      await new Promise(r => setTimeout(r, 800))

                      try {
                        const existingAlerts = JSON.parse(localStorage.getItem('bb_price_alerts') || '[]')
                        const newAlert = {
                          id: Date.now(),
                          productId: product.id,
                          productName: product.name,
                          productBrand: product.brand,
                          productImage: product.image,
                          bestPrice: product.bestPrice,
                          targetPrice: targetPrice,
                          platforms: trackedPlatforms,
                          email: alertEmail.trim(),
                          createdAt: new Date().toISOString()
                        }
                        localStorage.setItem('bb_price_alerts', JSON.stringify([newAlert, ...existingAlerts]))
                      } catch (err) {
                        console.error(err)
                      }

                      setIsAlertSubmitting(false)
                      setAlertSuccess(true)
                      setTimeout(() => {
                        setShowTrackModal(false)
                      }, 1800)
                    }}
                    className="space-y-4"
                  >
                    <div>
                      <label className="text-[0.7rem] font-mono font-medium uppercase tracking-[0.15em] text-[#a1a1aa] block mb-2">Notification Email</label>
                      <input
                        type="email"
                        required
                        value={alertEmail}
                        onChange={e => setAlertEmail(e.target.value)}
                        placeholder="OPERATIVE@SECURITY.IO"
                        className="w-full bg-[#141418] border border-[#27272a] rounded-xl px-4 py-3.5 focus:border-[#f20ab0] focus:outline-none text-[0.875rem] font-mono tracking-widest text-white placeholder:text-[#3f3f46] uppercase text-center"
                      />
                    </div>

                    <button
                      type="submit"
                      disabled={isAlertSubmitting || !alertEmail.trim()}
                      className="w-full py-4 text-[0.75rem] font-mono font-bold uppercase tracking-[0.2em] bg-[#f20ab0] text-white rounded-xl hover:bg-[#d00896] transition-all duration-300 disabled:opacity-20 disabled:cursor-not-allowed shadow-[0_0_25px_rgba(242,10,176,0.3)]"
                    >
                      {isAlertSubmitting ? 'Initializing Radar...' : 'Activate Price Radar'}
                    </button>
                  </form>
                </>
              )}
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  )
}

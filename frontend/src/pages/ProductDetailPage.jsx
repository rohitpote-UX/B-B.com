import { useState, useMemo, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { ArrowLeft, ArrowUpRight } from 'lucide-react'
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'
import { PRODUCTS, PLATFORMS, generatePriceHistory, formatPrice } from '../data/demoData'

export default function ProductDetailPage() {
  const { id } = useParams()
  const product = PRODUCTS.find(p => p.id === parseInt(id)) || PRODUCTS[0]
  const priceHistory = useMemo(() => generatePriceHistory(product.bestPrice), [product])
  
  const suggestedProduct = useMemo(() => {
    const similarProducts = PRODUCTS.filter(p => p.category === product.category && p.id !== product.id);
    similarProducts.sort((a, b) => Math.abs(a.bestPrice - product.bestPrice) - Math.abs(b.bestPrice - product.bestPrice));
    return similarProducts[0] || PRODUCTS.find(p => p.id !== product.id) || PRODUCTS[1];
  }, [product]);

  // Price Tracking State Variables
  const [showTrackModal, setShowTrackModal] = useState(false)
  const [targetPrice, setTargetPrice] = useState(Math.round(product.bestPrice * 0.9))
  const [trackedPlatforms, setTrackedPlatforms] = useState(product.prices.map(p => p.platform))
  const [isAlertSubmitting, setIsAlertSubmitting] = useState(false)
  const [alertSuccess, setAlertSuccess] = useState(false)
  const [alertEmail, setAlertEmail] = useState('')

  useEffect(() => {
    setTargetPrice(Math.round(product.bestPrice * 0.9))
    setTrackedPlatforms(product.prices.map(p => p.platform))
    setAlertSuccess(false)
  }, [product.id, product.bestPrice])
  
  return (
    <div className="min-h-screen pt-40 pb-56">
      <div className="w-full max-w-[1536px] mx-auto px-8 md:px-16">
        {/* Minimal Navigation */}
        <Link to="/search" className="inline-flex items-center gap-4 text-[0.75rem] font-medium uppercase tracking-[0.15em] text-theme-muted hover:text-theme-text transition-colors mb-20">
           <ArrowLeft className="w-4 h-4" /> BACK TO CATALOG
        </Link>

        {/* Hero Product View - Split Layout */}
        <div className="grid grid-cols-12 gap-8 lg:gap-16 items-center mb-48">
           {/* Visual */}
           <div className="col-span-12 lg:col-span-6 bg-theme-elevated aspect-square flex items-center justify-center p-20 lg:p-32 overflow-hidden group">
              <motion.img 
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 1, ease: [0.22, 1, 0.36, 1] }}
                src={product.image} 
                alt={product.name} 
                className="max-w-full max-h-full object-contain filter drop-shadow-2xl group-hover:scale-110 transition-transform duration-[1.5s]" 
              />
           </div>

           {/* Details */}
           <div className="col-span-12 lg:col-span-5 lg:col-start-8 py-16 lg:py-0">
              <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.8, delay: 0.2 }}>
                 <span className="text-[0.75rem] font-medium uppercase tracking-[0.15em] block mb-8">{product.brand} · {product.category}</span>
                 <h1 className="text-[3rem] sm:text-[4.5rem] lg:text-[5.5rem] font-[var(--font-display)] font-medium leading-[1.05] tracking-tight text-theme-text mb-12 tracking-tight leading-none">{product.name}</h1>
                 
                 <div className="flex items-baseline gap-6 mb-16 pb-16 border-b border-theme-border">
                    <span className="text-[2.5rem] font-medium text-theme-text">{formatPrice(product.bestPrice)}</span>
                    <span className="text-[1.25rem] text-theme-muted line-through">{formatPrice(product.originalPrice)}</span>
                 </div>

                 <p className="text-[1.125rem] sm:text-[1.25rem] leading-[1.6] tracking-tight text-theme-secondary mb-20 leading-relaxed">
                   {product.description}
                 </p>

                 <div className="flex flex-col sm:flex-row gap-4">
                    <button className="inline-flex items-center justify-center px-10 py-5 bg-transparent border border-theme-text text-theme-text text-[0.875rem] font-medium tracking-wide transition-all duration-300 rounded-[2px] hover:bg-theme-text hover:text-theme-bg w-full sm:w-auto px-12">
                       Purchase Now
                    </button>
                    <Link to={`/compare?p1=${product.id}&p2=${suggestedProduct.id}`} className="inline-flex items-center justify-center px-10 py-5 bg-transparent border border-theme-border text-theme-text text-[0.875rem] font-medium tracking-wide transition-all duration-300 rounded-[2px] hover:border-theme-text w-full sm:w-auto flex items-center gap-2">
                       Compare
                    </Link>
                    <button onClick={() => setShowTrackModal(true)} className="inline-flex items-center justify-center px-10 py-5 bg-transparent border border-theme-border text-theme-text text-[0.875rem] font-medium tracking-wide transition-all duration-300 rounded-[2px] hover:border-theme-text w-full sm:w-auto flex items-center gap-2">
                       Track Price
                    </button>
                 </div>
              </motion.div>
           </div>
        </div>

        {/* Detailed Information Split */}
        <div className="grid grid-cols-12 gap-8 lg:gap-16 border-t border-theme-border pt-40">
           {/* Left Column: Specs */}
           <div className="col-span-12 lg:col-span-4 mb-32 lg:mb-0">
              <h3 className="text-[2rem] sm:text-[3rem] lg:text-[3.5rem] font-medium leading-[1.1] tracking-tight text-theme-text mb-16">Specifications.</h3>
              <ul className="space-y-8">
                 {Object.entries(product.specs).map(([key, value]) => (
                    <li key={key} className="flex flex-col gap-2 border-b border-theme-border pb-8">
                       <span className="text-[0.75rem] font-medium uppercase tracking-[0.15em] text-theme-muted">{key}</span>
                       <span className="text-[1.125rem] text-theme-text">{String(value)}</span>
                    </li>
                 ))}
              </ul>
           </div>

           {/* Right Column: Analytics & Comparisons */}
           <div className="col-span-12 lg:col-span-7 lg:col-start-6 space-y-24">
              
              {/* Market Pricing */}
              <div>
                 <h3 className="text-[2rem] sm:text-[3rem] lg:text-[3.5rem] font-medium leading-[1.1] tracking-tight text-theme-text mb-12">Market Providers.</h3>
                 <div className="flex flex-col">
                    {product.prices.sort((a,b) => a.price - b.price).map((p, i) => (
                       <a key={p.platform} href="#" className={`flex items-center justify-between py-6 border-b border-theme-border group ${i===0 ? 'text-theme-text' : 'text-theme-secondary hover:text-theme-text transition-colors'}`}>
                          <div className="flex items-center gap-6">
                             <span className="text-[0.75rem] font-medium uppercase tracking-[0.15em] w-4 opacity-50">0{i+1}</span>
                             <span className="text-[1.125rem] font-medium">{PLATFORMS[p.platform]?.name}</span>
                          </div>
                          <div className="flex items-center gap-8 text-right">
                             <div>
                                <span className="block text-[1.125rem] font-medium">{formatPrice(p.price)}</span>
                                {i !== 0 && <span className="text-[0.75rem] text-theme-muted">+{Math.round(((p.price - product.bestPrice)/product.bestPrice)*100)}% premium</span>}
                             </div>
                             <ArrowUpRight className={`w-5 h-5 transition-transform duration-300 group-hover:translate-x-1 group-hover:-translate-y-1 ${i===0 ? 'text-theme-text' : 'text-theme-dim group-hover:text-theme-text'}`} />
                          </div>
                       </a>
                    ))}
                 </div>
              </div>

              {/* Price Graph */}
              <div>
                 <div className="flex items-end justify-between mb-12">
                    <h3 className="text-[2rem] sm:text-[3rem] lg:text-[3.5rem] font-medium leading-[1.1] tracking-tight text-theme-text">90-Day Analysis.</h3>
                 </div>
                 <div className="h-[400px] w-full bg-theme-elevated p-6 lg:p-8">
                    <ResponsiveContainer width="100%" height="100%">
                       <AreaChart data={priceHistory.filter((_, i) => i % 4 === 0)}>
                          <XAxis dataKey="date" tickLine={false} axisLine={false} tick={{ fontSize: 10, fill: '#737373' }} tickFormatter={v => v.slice(5)} dy={10} />
                          <YAxis tickLine={false} axisLine={false} tick={{ fontSize: 10, fill: '#737373' }} domain={['dataMin - 20', 'dataMax + 20']} dx={-10} />
                          <Tooltip contentStyle={{ background: '#0a0a0a', border: '1px solid #262626', borderRadius: '2px', fontSize: '12px' }} />
                          <Area type="monotone" dataKey="amazon" stroke="#ffffff" strokeWidth={2} fill="rgba(255,255,255,0.05)" />
                          <Area type="monotone" dataKey="flipkart" stroke="#737373" strokeWidth={2} fill="transparent" strokeDasharray="4 4" />
                       </AreaChart>
                    </ResponsiveContainer>
                 </div>
                 <div className="flex justify-end gap-6 mt-6">
                    <div className="flex items-center gap-3">
                       <span className="w-3 h-[2px] bg-theme-text"></span>
                       <span className="text-[0.75rem] font-medium uppercase tracking-[0.15em] text-theme-secondary">Amazon Pricing</span>
                    </div>
                    <div className="flex items-center gap-3">
                       <span className="w-3 h-[2px] bg-theme-dim border-dashed border-b border-[#737373]"></span>
                       <span className="text-[0.75rem] font-medium uppercase tracking-[0.15em] text-theme-secondary">Competitors Average</span>
                    </div>
                 </div>
              </div>

           </div>
        </div>
      </div>

        {/* ─── Track Price Modal ─── */}
        <AnimatePresence>
          {showTrackModal && (
            <div className="fixed inset-0 z-50 flex items-center justify-center p-6">
              {/* Backdrop */}
              <motion.div 
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                onClick={() => setShowTrackModal(false)}
                className="absolute inset-0 bg-black/80 backdrop-blur-md"
              />
              
              {/* Modal Container */}
              <motion.div 
                initial={{ opacity: 0, scale: 0.95, y: 20 }}
                animate={{ opacity: 1, scale: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.95, y: 20 }}
                transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
                className="relative bg-theme-bg border border-theme-border/60 rounded-3xl p-8 max-w-lg w-full z-10 shadow-[0_20px_50px_rgba(0,0,0,0.8)] overflow-hidden"
              >
                {/* Visual Glass highlights */}
                <div className="absolute -top-32 -right-32 w-64 h-64 bg-theme-text opacity-[0.03] blur-3xl rounded-full pointer-events-none" />
                <div className="absolute -bottom-32 -left-32 w-64 h-64 bg-[#22c55e] opacity-[0.03] blur-3xl rounded-full pointer-events-none" />

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
                          transition={{ delay: 0.2, type: "spring", stiffness: 200 }}
                          className="text-4xl text-[#22c55e]"
                        >✓</motion.span>
                     </div>
                     <h2 className="text-[2rem] font-[var(--font-display)] font-medium leading-[1.2] text-theme-text mb-4 uppercase tracking-wider">ALERT ACTIVATED.</h2>
                     <p className="text-theme-secondary text-[0.875rem] leading-relaxed max-w-xs mb-8">
                       Our price tracking engine will monitor this product 24/7 across selected platforms and notify you instantly.
                     </p>
                     <div className="px-5 py-2 bg-theme-elevated rounded-full border border-theme-border text-[0.75rem] font-mono text-theme-muted uppercase tracking-widest">
                       Target: {formatPrice(targetPrice)}
                     </div>
                  </motion.div>
                ) : (
                  <>
                    {/* Header */}
                    <div className="flex justify-between items-start mb-8">
                       <div>
                          <span className="text-[0.65rem] font-mono font-medium uppercase tracking-[0.2em] text-theme-muted block mb-2">Automated Radar</span>
                          <h2 className="text-[2rem] font-[var(--font-display)] font-medium leading-[1.1] text-theme-text uppercase tracking-tight">Track Price.</h2>
                       </div>
                       <button onClick={() => setShowTrackModal(false)} className="w-10 h-10 rounded-full border border-theme-border flex items-center justify-center hover:bg-theme-elevated transition-colors text-theme-muted hover:text-theme-text text-[0.875rem]">
                          ✕
                       </button>
                    </div>

                    {/* Product Summary */}
                    <div className="flex items-center gap-4 bg-theme-elevated/40 border border-theme-border/50 rounded-2xl p-4 mb-6">
                       <div className="w-16 h-16 bg-theme-elevated p-2 rounded-xl flex items-center justify-center shrink-0">
                          <img src={product.image} className="max-w-full max-h-full object-contain mix-blend-normal" />
                       </div>
                       <div className="min-w-0 flex-1">
                          <p className="text-[0.65rem] font-bold uppercase tracking-widest text-theme-muted mb-0.5">{product.brand}</p>
                          <h4 className="font-medium text-theme-text text-[0.875rem] truncate">{product.name}</h4>
                          <p className="text-[0.75rem] font-medium text-theme-secondary mt-1">Current best: {formatPrice(product.bestPrice)}</p>
                       </div>
                    </div>

                    {/* AI Diagnostic Alert */}
                    <div className="mb-6 bg-theme-elevated/20 border border-theme-border/30 rounded-xl p-4 flex gap-3">
                       <span className="text-[1.25rem]">{product.dealScore >= 85 ? "🟢" : "🟡"}</span>
                       <div>
                          <span className="text-[0.65rem] font-bold uppercase tracking-widest text-theme-text block mb-1">
                             {product.dealScore >= 85 ? "Buy Signal Active" : "Hold Signal / High Tracker Recommendation"}
                          </span>
                          <p className="text-[0.75rem] text-theme-secondary leading-relaxed">
                             {product.dealScore >= 85 
                               ? `This item has a premium deal score of ${product.dealScore}/100. Price is near historical low, but tracking is active.` 
                               : "This product is currently at standard pricing. Setting a price alert is highly advised to catch the next drop."}
                          </p>
                       </div>
                    </div>

                    {/* Slider Target */}
                    <div className="mb-8">
                       <div className="flex justify-between items-baseline mb-3">
                          <label className="text-[0.7rem] font-mono font-medium uppercase tracking-[0.15em] text-theme-secondary">Target Price</label>
                          <span className="text-[1.125rem] font-bold font-mono text-[#22c55e]">
                             {formatPrice(targetPrice)}
                             <span className="text-[0.75rem] text-theme-muted font-normal ml-2">
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
                         onChange={(e) => setTargetPrice(parseInt(e.target.value))}
                         className="w-full h-1 bg-theme-subtle rounded-lg appearance-none cursor-pointer accent-[#22c55e]"
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
                                 className={`flex-1 py-2 text-[0.65rem] font-mono font-medium uppercase tracking-widest border transition-all duration-300 rounded-[2px] ${
                                   targetPrice === presetVal 
                                     ? 'bg-[#22c55e]/10 border-[#22c55e]/40 text-[#22c55e]' 
                                     : 'bg-transparent text-theme-muted border-theme-border hover:border-theme-text hover:text-theme-text'
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
                       <label className="text-[0.7rem] font-mono font-medium uppercase tracking-[0.15em] text-theme-secondary block mb-3">Monitor Providers</label>
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
                                     ? 'bg-theme-text text-theme-bg border-theme-text font-semibold' 
                                     : 'bg-transparent text-theme-muted border-theme-border hover:border-theme-text'
                                 }`}
                               >
                                 <span>{PLATFORMS[p.platform]?.icon}</span>
                                 <span>{PLATFORMS[p.platform]?.name}</span>
                               </button>
                             )
                          })}
                       </div>
                    </div>

                    {/* Email Capture & Submit */}
                    <form onSubmit={async (e) => {
                       e.preventDefault()
                       if (!alertEmail.trim()) return
                       setIsAlertSubmitting(true)
                       await new Promise(r => setTimeout(r, 1000))
                       
                       // Push alert to localStorage
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
                    }} className="space-y-4">
                       <div>
                          <label className="text-[0.7rem] font-mono font-medium uppercase tracking-[0.15em] text-theme-secondary block mb-2">Notification Email</label>
                          <input 
                            type="email" 
                            required
                            value={alertEmail}
                            onChange={(e) => setAlertEmail(e.target.value)}
                            placeholder="OPERATIVE@SECURITY.IO"
                            className="w-full bg-theme-elevated/40 border border-theme-border rounded-lg px-4 py-3.5 focus:border-[#22c55e]/50 focus:outline-none text-[0.875rem] font-mono tracking-widest text-theme-text placeholder:text-theme-dim uppercase text-center"
                          />
                       </div>
                       
                       <button 
                         type="submit" 
                         disabled={isAlertSubmitting || !alertEmail.trim()}
                         className="w-full py-4 text-[0.75rem] font-mono font-bold uppercase tracking-[0.2em] bg-theme-text text-theme-bg rounded-[4px] hover:scale-[1.02] transition-all duration-300 disabled:opacity-20 disabled:cursor-not-allowed hover:bg-[#22c55e] hover:text-black hover:shadow-[0_0_25px_rgba(34,197,94,0.3)]"
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

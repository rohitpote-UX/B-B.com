'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { motion } from 'framer-motion'
import { Settings, Heart, Cpu, ArrowRight } from 'lucide-react'
import { PRODUCTS, formatPrice } from '@/data/demoData'
import { Product, PriceAlert } from '@/types'

export default function ProfilePage() {
  const [interest, setInterest] = useState('None')
  const [savedProducts, setSavedProducts] = useState<Product[]>([])
  const [selectedCategory, setSelectedCategory] = useState('All')
  const [priceAlerts, setPriceAlerts] = useState<PriceAlert[]>([])

  useEffect(() => {
    // Load Behavioral Algorithms
    setInterest(localStorage.getItem('bb_user_interest') || 'None')
    try {
      const savedIds = JSON.parse(localStorage.getItem('bb_liked_products') || '[]')
      // Normalize unique IDs (e.g. "223-0") and strings to simple product IDs
      const normalizedIds = savedIds.map((id: string | number) => {
        if (typeof id === 'string' && id.includes('-')) {
          return parseInt(id.split('-')[0]);
        }
        return typeof id === 'string' ? parseInt(id) : id;
      });
      // Map IDs back to full products
      const products = (PRODUCTS as unknown as Product[]).filter(p => normalizedIds.includes(p.id))
      setSavedProducts(products)
    } catch { setSavedProducts([]) }

    // Load price alerts
    try {
      const savedAlerts = JSON.parse(localStorage.getItem('bb_price_alerts') || '[]')
      setPriceAlerts(savedAlerts)
    } catch { setPriceAlerts([]) }
  }, [])

  const categories = ['All', ...Array.from(new Set(savedProducts.map(p => p.category)))]
  
  const filteredProducts = selectedCategory === 'All'
    ? savedProducts
    : savedProducts.filter(p => p.category === selectedCategory)

  // Replicate brand names and styling correctly
  const PLATFORMS: Record<string, { name: string }> = {
    amazon: { name: 'Amazon' },
    flipkart: { name: 'Flipkart' },
    myntra: { name: 'Myntra' },
    ajio: { name: 'Ajio' },
    croma: { name: 'Croma' },
    reliance_digital: { name: 'Reliance Digital' },
    brand_store: { name: 'Brand Store' }
  }

  return (
    <motion.div 
      initial={{ opacity: 0 }} 
      animate={{ opacity: 1 }} 
      transition={{ duration: 0.8 }}
      className="min-h-[100dvh] pt-32 pb-40 px-6 md:px-12 max-w-[1536px] mx-auto"
    >
      {/* Header */}
      <div className="flex justify-between items-center mb-16">
         <h1 className="text-4xl md:text-6xl font-[var(--font-display)] font-medium tracking-tight">OPERATIVE <span className="text-theme-secondary">DASHBOARD</span></h1>
         <button className="w-12 h-12 rounded-full border border-theme-border flex items-center justify-center hover:bg-theme-elevated transition-colors">
            <Settings className="w-5 h-5 text-theme-text" />
         </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 lg:gap-8">
         
         {/* Identity Card */}
         <div className="md:col-span-2 bg-theme-elevated border border-theme-border rounded-[2rem] p-8 md:p-12 relative overflow-hidden flex flex-col justify-between min-h-[300px]">
            <div className="relative z-10 flex justify-between items-start">
               <div>
                  <h2 className="text-3xl font-medium tracking-tight mb-2">Guest Iteration</h2>
                  <p className="text-theme-secondary text-[0.875rem] uppercase tracking-widest font-mono">ID: BB-089-X</p>
               </div>
               <div className="px-4 py-1.5 bg-[#22c55e]/10 border border-[#22c55e]/20 text-[#22c55e] text-[0.65rem] font-bold uppercase tracking-widest rounded-full">
                  Status: Premium Active
               </div>
            </div>
            
            <div className="relative z-10 grid grid-cols-2 md:grid-cols-4 gap-8 mt-16">
               <div>
                  <div className="text-[0.65rem] uppercase tracking-widest text-theme-muted mb-2 font-mono">Total Saved</div>
                  <div className="text-3xl font-[var(--font-display)]">{savedProducts.length}</div>
               </div>
                <div>
                   <div className="text-[0.65rem] uppercase tracking-widest text-theme-muted mb-2 font-mono">Active Alerts</div>
                   <div className="text-3xl font-[var(--font-display)]">{priceAlerts.length}</div>
                </div>
               <div>
                  <div className="text-[0.65rem] uppercase tracking-widest text-theme-muted mb-2 font-mono">Total Savings</div>
                  <div className="text-3xl font-[var(--font-display)] text-[#22c55e]">{formatPrice(420)}</div>
               </div>
            </div>

            {/* Decoration */}
            <div className="absolute -bottom-24 -right-24 w-96 h-96 bg-theme-text opacity-5 blur-[100px] rounded-full pointer-events-none" />
         </div>

         {/* AI Profiling Card */}
         <div className="bg-theme-bg border border-theme-border rounded-[2rem] p-8 md:p-12 flex flex-col justify-between relative overflow-hidden group hover:border-[#22c55e]/50 transition-colors">
            <div className="relative z-10">
               <div className="flex items-center gap-3 mb-8">
                  <Cpu className="w-5 h-5 text-theme-text group-hover:text-[#22c55e] transition-colors" />
                  <span className="text-[0.65rem] uppercase tracking-widest font-mono text-theme-secondary">Algorithm Profiling</span>
               </div>
               <p className="text-[0.875rem] text-theme-muted leading-relaxed">
                  Based on your neural interaction patterns, the AI is currently tailoring your global Discovery feed for:
               </p>
               <div className="mt-8 text-xl sm:text-2xl font-[var(--font-display)] tracking-tight text-theme-text bg-theme-elevated inline-block px-6 py-3 rounded-full border border-theme-border flex items-center gap-4 w-max shadow-[0_10px_30px_rgba(0,0,0,0.5)]">
                  {interest.toUpperCase()}
                  <span className="w-2 h-2 rounded-full bg-[#22c55e] animate-pulse" />
               </div>
            </div>
         </div>

          {/* Active Price Radars */}
          <div className="md:col-span-3 bg-theme-bg border border-theme-border rounded-[2rem] p-8 md:p-12 mt-4">
             <div className="flex items-center justify-between mb-8">
                <div className="flex items-center gap-3">
                   <Cpu className="w-5 h-5 text-[#22c55e]" />
                   <span className="text-[0.65rem] uppercase tracking-widest font-mono text-theme-text">Active Price Radars</span>
                </div>
                <span className="text-[0.65rem] uppercase tracking-widest font-mono text-theme-muted">{priceAlerts.length} Radar Nodes Online</span>
             </div>
             
             {priceAlerts.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                   {priceAlerts.map((alert) => (
                      <div key={alert.id} className="bg-theme-elevated border border-theme-border rounded-2xl p-6 relative flex flex-col justify-between overflow-hidden group hover:border-[#22c55e]/40 transition-colors duration-500">
                          {/* Glow decorative point */}
                          <div className="absolute top-4 right-4 w-1.5 h-1.5 rounded-full bg-[#22c55e] animate-pulse" />
                          
                          <div>
                             <div className="flex gap-4 items-center mb-4">
                                <div className="w-14 h-14 bg-theme-bg p-2 rounded-xl flex items-center justify-center shrink-0 border border-theme-border">
                                   <img src={alert.productImage} className="max-w-full max-h-full object-contain mix-blend-normal" alt={alert.productName} />
                                </div>
                                <div className="min-w-0">
                                   <span className="text-[0.6rem] font-mono font-medium uppercase tracking-[0.15em] text-theme-muted block mb-0.5">{alert.productBrand}</span>
                                   <h4 className="font-semibold text-theme-text text-[0.875rem] truncate pr-4">{alert.productName}</h4>
                                </div>
                             </div>

                             <div className="grid grid-cols-2 gap-4 border-t border-b border-theme-border/40 py-4 my-4">
                                <div>
                                   <span className="text-[0.6rem] font-mono text-theme-muted uppercase tracking-wider block mb-1">Radar Target</span>
                                   <span className="text-[1rem] font-bold font-mono text-[#22c55e]">{formatPrice(alert.targetPrice)}</span>
                                </div>
                                <div>
                                   <span className="text-[0.6rem] font-mono text-theme-muted uppercase tracking-wider block mb-1">Current Best</span>
                                   <span className="text-[1rem] font-bold font-mono text-theme-text">{formatPrice(alert.bestPrice)}</span>
                                </div>
                             </div>

                             <div className="flex flex-wrap gap-1.5 mb-6">
                                {alert.platforms.map(pl => (
                                   <span key={pl} className="px-2 py-1 bg-theme-bg/60 border border-theme-border text-[0.55rem] font-mono text-theme-muted uppercase tracking-widest rounded-full">
                                      {PLATFORMS[pl]?.name || pl}
                                   </span>
                                 ))}
                             </div>
                          </div>

                          <div className="flex justify-between items-center pt-4 border-t border-theme-border/40">
                             <span className="text-[0.55rem] font-mono text-theme-muted uppercase tracking-widest">Radar: {alert.email}</span>
                             <button 
                               onClick={() => {
                                  const newAlerts = priceAlerts.filter(a => a.id !== alert.id)
                                  setPriceAlerts(newAlerts)
                                  localStorage.setItem('bb_price_alerts', JSON.stringify(newAlerts))
                               }}
                               className="text-[0.65rem] font-mono font-semibold uppercase tracking-wider text-red-500 hover:text-red-400 hover:underline transition-colors"
                             >
                                Deactivate
                             </button>
                          </div>
                      </div>
                   ))}
                </div>
             ) : (
                <div className="py-16 flex flex-col items-center justify-center text-center border border-dashed border-theme-border/50 rounded-xl bg-theme-elevated/20">
                   <p className="text-theme-text font-medium mb-2 font-mono uppercase tracking-widest text-[0.75rem]">No Active Radars</p>
                   <p className="text-[0.875rem] text-theme-secondary mb-6 max-w-sm">Use the &quot;Track Price&quot; system on any product's details page to establish price drop alert nodes.</p>
                   <Link href="/search" className="px-6 py-2.5 bg-theme-text text-theme-bg text-[0.65rem] font-bold uppercase tracking-widest rounded-[2px] transition-transform hover:scale-[1.05]">
                      Search Catalog
                   </Link>
                </div>
             )}
          </div>

         {/* Saved Arsenal */}
         <div className="md:col-span-3 bg-theme-bg border border-theme-border rounded-[2rem] p-8 md:p-12 mt-2">
            <div className="flex items-center justify-between mb-8">
               <div className="flex items-center gap-3">
                  <Heart className="w-5 h-5 text-theme-text fill-theme-text" />
                  <span className="text-[0.65rem] uppercase tracking-widest font-mono text-theme-text">Your Saved Arsenal</span>
               </div>
               <Link href="/discover" className="text-[0.75rem] uppercase tracking-widest text-theme-secondary hover:text-theme-text transition-colors flex items-center gap-2">
                  Discover More <ArrowRight className="w-3 h-3" />
               </Link>
            </div>
            
            {/* Category Filter Pills */}
             {savedProducts.length > 0 && (
                <div className="mb-10 flex gap-3 overflow-x-auto hide-scrollbar pb-2 border-b border-theme-border/30">
                  {categories.map(cat => (
                    <button 
                      key={cat} 
                      type="button" 
                      onClick={() => setSelectedCategory(cat)}
                      className={`shrink-0 px-5 py-2 text-[0.7rem] font-mono font-medium uppercase tracking-[0.12em] border transition-all duration-300 rounded-[2px] ${
                        selectedCategory === cat 
                          ? 'bg-theme-text text-theme-bg border-theme-text font-semibold shadow-md' 
                          : 'bg-transparent text-theme-secondary border-theme-border hover:border-theme-text hover:text-theme-text'
                      }`}
                    >
                      {cat} ({cat === 'All' ? savedProducts.length : savedProducts.filter(p => p.category === cat).length})
                    </button>
                  ))}
                </div>
             )}

              {filteredProducts.length > 0 ? (
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
                   {filteredProducts.map((p, idx) => (
                      <Link key={idx} href={`/product/${p.id}`} className="block group">
                         <div className="aspect-[4/3] bg-theme-elevated p-8 mb-4 border border-theme-border flex items-center justify-center overflow-hidden rounded-xl group-hover:border-theme-text/50 transition-colors">
                            <img src={p.image} className="max-w-full max-h-full object-contain mix-blend-normal group-hover:scale-110 transition-transform duration-700 ease-out" alt={p.name} />
                         </div>
                         <div className="flex justify-between items-start">
                            <div>
                               <p className="text-[0.65rem] font-bold uppercase tracking-widest text-theme-muted mb-1">{p.brand}</p>
                               <p className="font-medium text-[0.875rem] text-theme-text truncate max-w-[150px]">{p.name}</p>
                            </div>
                            <p className="text-[0.875rem] font-[var(--font-display)]">{formatPrice(p.bestPrice)}</p>
                          </div>
                      </Link>
                   ))}
                </div>
             ) : (
                <div className="py-24 flex flex-col items-center justify-center text-center border border-dashed border-theme-border/50 rounded-xl bg-theme-elevated/20">
                   <p className="text-theme-text font-medium mb-2">No hardware saved yet.</p>
                   <p className="text-[0.875rem] text-theme-secondary mb-6 max-w-sm">Tap the heart icon on any product in the Discover feed to push it to your personal arsenal.</p>
                   <Link href="/discover" className="px-6 py-2.5 bg-theme-text text-theme-bg text-[0.65rem] font-bold uppercase tracking-widest rounded-[2px] transition-transform hover:scale-[1.05]">
                      Launch Discover
                   </Link>
                </div>
             )}
          </div>

      </div>
    </motion.div>
  )
}

'use client'

import { useState, useRef, useEffect, useMemo } from 'react'
import { useRouter } from 'next/navigation'
import { motion, AnimatePresence } from 'framer-motion'
import { Heart, Share2, RefreshCcw } from 'lucide-react'
import { PRODUCTS, formatPrice } from '@/data/demoData'
import { Product } from '@/types'

export default function DiscoverClient() {
  const router = useRouter()
  
  // Algorithmic Engagement Feed based on User Search History
  const extendedFeed = useMemo(() => {
    try {
      const interest = localStorage.getItem('bb_user_interest') || 'Smartphones'
      
      const relatedCategories: Record<string, { rel: string[]; sim: string[] }> = {
        'Smartphones': { rel: ['Headphones', 'fashion and accessories'], sim: ['Laptops', 'electronics'] },
        'Laptops': { rel: ['Headphones', 'office wear'], sim: ['Smartphones', 'premium Products'] },
        'Shoes': { rel: ['mens wear', 'ladies wear', 'kids Wear'], sim: ['fashion and accessories'] },
        'mens wear': { rel: ['Shoes', 'fashion and accessories'], sim: ['office wear'] },
        'ladies wear': { rel: ['Shoes', 'fashion and accessories'], sim: ['premium Products'] },
        'Headphones': { rel: ['Smartphones', 'Laptops'], sim: ['electronics'] },
        'Home Appliance': { rel: ['everyday essential'], sim: ['electronics'] },
      }
      const mapping = relatedCategories[interest] || { rel: ['everyday essential', 'Headphones'], sim: ['Shoes', 'premium Products'] }
      
      const primary = (PRODUCTS as unknown as Product[]).filter(p => p.category === interest).sort(() => Math.random() - 0.5)
      const related = (PRODUCTS as unknown as Product[]).filter(p => mapping.rel.includes(p.category)).sort(() => Math.random() - 0.5)
      const similar = (PRODUCTS as unknown as Product[]).filter(p => mapping.sim.includes(p.category)).sort(() => Math.random() - 0.5)
      const trending = (PRODUCTS as unknown as Product[]).filter(p => p.dealScore >= 90).sort(() => Math.random() - 0.5)
      const smart = (PRODUCTS as unknown as Product[]).filter(p => p.rating >= 4.7).sort(() => Math.random() - 0.5)
      
      const generateChunk = () => {
         const getItems = (arr: Product[], count: number) => {
             const items = []
             for(let i=0; i<count; i++) {
                 if (arr.length === 0) break
                 items.push(arr.shift()!)
             }
             return items
         }
         return [
            ...getItems(primary, 4).map(p => ({...p, feedBadge: 'Based on your search'})),
            ...getItems(related, 3).map(p => ({...p, feedBadge: 'People also viewed'})),
            ...getItems(similar, 1).map(p => ({...p, feedBadge: 'Related Category'})),
            ...getItems(trending, 1).map(p => ({...p, feedBadge: 'Trending now'})),
            ...getItems(smart, 1).map(p => ({...p, feedBadge: 'New arrivals'}))
         ]
      }
      
      const loop = []
      for(let i=0; i<6; i++) {
         loop.push(...generateChunk())
         if (primary.length < 4) primary.push(...(PRODUCTS.filter(p => p.category === interest).sort(() => Math.random() - 0.5) as unknown as Product[]))
         if (related.length < 3) related.push(...(PRODUCTS.filter(p => mapping.rel.includes(p.category)).sort(() => Math.random() - 0.5) as unknown as Product[]))
         if (similar.length < 2) similar.push(...(PRODUCTS.filter(p => mapping.sim.includes(p.category)).sort(() => Math.random() - 0.5) as unknown as Product[]))
         if (trending.length < 2) trending.push(...(PRODUCTS.filter(p => p.dealScore >= 90).sort(() => Math.random() - 0.5) as unknown as Product[]))
         if (smart.length < 2) smart.push(...(PRODUCTS.filter(p => p.rating >= 4.7).sort(() => Math.random() - 0.5) as unknown as Product[]))
      }
      
      return loop.map((p, idx) => ({...p, uniqueId: `${p.id}-${idx}`}))
    } catch { return PRODUCTS.map((p, idx) => ({...p, uniqueId: `${p.id}-${idx}`})) }
  }, [])

  const [activeIdx, setActiveIdx] = useState(0)
  const [likedItems, setLikedItems] = useState<Set<string | number>>(() => {
    if (typeof window === 'undefined') return new Set()
    try {
      const saved = localStorage.getItem('bb_liked_products')
      return saved ? new Set(JSON.parse(saved)) : new Set()
    } catch { return new Set() }
  })
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    localStorage.setItem('bb_liked_products', JSON.stringify([...likedItems]))
  }, [likedItems])

  // Snap threshold observer
  const handleScroll = () => {
    if (!containerRef.current) return
    const index = Math.round(containerRef.current.scrollTop / window.innerHeight)
    if (index !== activeIdx) setActiveIdx(index)
  }

  const toggleLike = (id: number) => {
    const newLiked = new Set(likedItems)
    if (newLiked.has(id)) newLiked.delete(id)
    else if (newLiked.has(id.toString())) newLiked.delete(id.toString())
    else newLiked.add(id)
    setLikedItems(newLiked)
  }

  const handleShare = async (product: Product) => {
    const shareData = {
      title: `Brand Battle: ${product.name}`,
      text: `Found a massive deal on the ${product.name} for $${product.bestPrice} (₹${Math.round(product.bestPrice * 84).toLocaleString()})!`,
      url: window.location.origin + `/product/${product.id}`
    }
    if (navigator.share) {
      try { await navigator.share(shareData) } catch (err) { console.error(err) }
    } else {
      navigator.clipboard.writeText(shareData.url)
      alert("Link copied to clipboard!")
    }
  }

  const handleCompare = (product: Product) => {
    const peers = PRODUCTS.filter(p => p.category === product.category && p.id !== product.id)
    const peerId = peers.length > 0 ? peers[0].id : ''
    router.push(`/compare?p1=${product.id}&p2=${peerId}`)
  }

  return (
    <div 
      ref={containerRef}
      onScroll={handleScroll}
      className="fixed inset-0 top-0 z-40 bg-theme-bg overflow-y-scroll snap-y snap-mandatory hide-scrollbar"
      style={{ height: '100vh', scrollBehavior: 'smooth' }}
    >
      {/* Dynamic Background subtle overlay */}
      <div className="fixed inset-0 pointer-events-none z-0 bg-[radial-gradient(circle_at_center,theme(colors.theme-elevated)_0%,theme(colors.theme-bg)_100%)] opacity-30" />

      {extendedFeed.map((productRaw, index) => {
         const product = productRaw as any
         const isActive = index === activeIdx
         const isLiked = likedItems.has(product.id) || likedItems.has(product.id.toString())

         return (
           <div key={product.uniqueId} className="w-full h-screen h-[100dvh] snap-center relative flex items-center justify-center sm:p-8 z-10 overflow-hidden">
              
              {/* Layout Container */}
              <div className="w-full h-full sm:max-w-[420px] md:max-w-[480px] sm:h-[90vh] bg-theme-elevated relative flex flex-col justify-between overflow-hidden sm:rounded-[2rem] sm:border border-theme-border shadow-2xl">
                 
                 <AnimatePresence>
                   {isActive && (
                      <motion.div 
                        initial={{ opacity: 0, scale: 0.95 }}
                        animate={{ opacity: 1, scale: 1 }}
                        exit={{ opacity: 0, scale: 1.05 }}
                        transition={{ duration: 0.8, ease: [0.22, 1, 0.36, 1] }}
                        className="w-full h-full relative"
                      >
                         <div className="absolute top-6 left-6 flex flex-col gap-2 z-20">
                            {product.feedBadge && (
                               <div className="px-4 py-2 w-max bg-theme-text/90 backdrop-blur-md border border-theme-bg/20 text-theme-bg text-[0.65rem] font-bold uppercase tracking-widest rounded-full shadow-xl">
                                  ★ {product.feedBadge}
                               </div>
                            )}
                            <div className="px-4 py-2 w-max bg-theme-bg/80 backdrop-blur-md border border-theme-border text-theme-text text-[0.65rem] font-medium uppercase tracking-widest rounded-full">
                               {product.brand}
                            </div>
                         </div>

                         {/* Fake "Loading AI Algorithm" scanning line */}
                         <motion.div 
                            initial={{ top: '-10%' }}
                            animate={{ top: '110%' }}
                            transition={{ duration: 2.5, repeat: Infinity, ease: "linear" }}
                            className="absolute left-0 right-0 h-[1px] bg-theme-text/20 z-0 shadow-[0_2px_20px_var(--color-theme-text)] pointer-events-none"
                         />
                         
                         {/* Premium Framed Image Showcase Box */}
                         <div className="absolute top-20 left-6 right-6 h-[38%] bg-theme-bg/40 backdrop-blur-md border border-theme-border/50 rounded-2xl flex items-center justify-center p-4 z-10 overflow-hidden group/img">
                            <img src={product.image} className="max-w-full max-h-full object-contain filter drop-shadow-2xl group-hover/img:scale-105 transition-transform duration-[2s] ease-out mix-blend-normal" alt={product.name} />
                         </div>
                         
                         {/* Product Information Overlay with higher opacity background gradient */}
                         <div className="absolute bottom-0 left-0 right-0 flex items-end justify-between w-full h-[54%] bg-gradient-to-t from-theme-bg via-theme-bg/95 to-transparent z-20 p-6 pt-12 pb-safe">
                            
                            {/* Left Text & Deals - min-w-0 guarantees flexible layout width */}
                            <div className="flex-1 min-w-0 pr-4">
                               <h2 className="text-[1.6rem] font-[var(--font-display)] font-medium leading-[1.15] text-theme-text tracking-tight mb-2 line-clamp-2 break-words" title={product.name}>{product.name}</h2>
                               <p className="text-[0.875rem] text-theme-secondary mb-6 line-clamp-2 pr-4">{product.specs.processor || product.specs.panel || 'Premium hardware engineered for uncompromising performance and precision.'}</p>
                               
                               <div className="flex flex-col gap-3">
                                  {/* Best Deal */}
                                  <div className="flex items-center gap-3 border-l-2 border-[#22c55e] pl-3 py-1">
                                     <div>
                                        <div className="text-[0.65rem] font-medium uppercase tracking-[0.1em] text-theme-secondary flex items-center gap-1">
                                           Best Deal Discovered
                                        </div>
                                        <div className="text-[1.75rem] font-[var(--font-display)] font-medium text-theme-text leading-none mt-1 group-hover:text-[#22c55e] transition-colors">{formatPrice(product.bestPrice)}</div>
                                     </div>
                                     <div className="ml-auto px-3 py-1.5 bg-[#22c55e]/10 text-[#22c55e] border border-[#22c55e]/20 text-[0.65rem] font-medium uppercase tracking-widest rounded-full">Amazon</div>
                                  </div>

                                  {/* Alternative Deals List */}
                                  <div className="flex items-center gap-2 mt-2 w-full">
                                     <div className="flex-1 flex justify-between items-center py-2 px-3 bg-theme-bg/50 backdrop-blur-md border border-theme-border rounded-[4px]">
                                        <span className="text-[0.65rem] uppercase tracking-widest text-theme-muted">Best Buy</span>
                                        <span className="text-[0.75rem] font-medium text-theme-secondary">{formatPrice(product.bestPrice + 49)}</span>
                                     </div>
                                     <div className="flex-1 flex justify-between items-center py-2 px-3 bg-theme-bg/50 backdrop-blur-md border border-theme-border rounded-[4px]">
                                        <span className="text-[0.65rem] uppercase tracking-widest text-theme-muted">Target</span>
                                        <span className="text-[0.75rem] font-medium text-theme-secondary">{formatPrice(product.bestPrice + 99)}</span>
                                     </div>
                                  </div>
                               </div>
                            </div>
                            
                            {/* Interaction Strip (Reels Style) - shrink-0 prevents layout squashing */}
                            <div className="flex flex-col gap-4 items-center pb-2 pl-2 shrink-0 z-30">
                               <button 
                                  onClick={() => toggleLike(product.id)} 
                                  className="group flex flex-col items-center gap-1"
                                >
                                   <div className={`w-12 h-12 rounded-full flex items-center justify-center transition-colors duration-300 ${isLiked ? 'bg-theme-text text-theme-bg shadow-[0_0_20px_rgba(255,255,255,0.2)]' : 'bg-theme-bg/80 backdrop-blur-md border border-theme-border text-theme-text hover:bg-theme-strong'}`}>
                                      <Heart className={`w-5 h-5 ${isLiked ? 'fill-current' : ''}`} strokeWidth={1.5} />
                                   </div>
                                   <span className="text-[0.55rem] text-theme-text font-medium tracking-widest uppercase">{isLiked ? 'Saved' : 'Save'}</span>
                                </button>

                                <button onClick={() => handleCompare(product)} className="group flex flex-col items-center gap-1 mt-2">
                                   <div className="w-12 h-12 rounded-full flex items-center justify-center bg-theme-bg/80 backdrop-blur-md border border-theme-border text-theme-text hover:bg-theme-strong transition-colors duration-300">
                                      <RefreshCcw className="w-5 h-5" strokeWidth={1.5} />
                                   </div>
                                   <span className="text-[0.55rem] text-theme-text font-medium tracking-widest uppercase">Compare</span>
                                </button>

                                <button onClick={() => handleShare(product)} className="group flex flex-col items-center gap-1 mt-2">
                                   <div className="w-12 h-12 rounded-full flex items-center justify-center bg-theme-bg/80 backdrop-blur-md border border-theme-border text-theme-text hover:bg-theme-strong transition-colors duration-300">
                                      <Share2 className="w-5 h-5" strokeWidth={1.5} />
                                   </div>
                                   <span className="text-[0.55rem] text-theme-text font-medium tracking-widest uppercase">Share</span>
                                </button>
                            </div>

                         </div>
                      </motion.div>
                   )}
                 </AnimatePresence>
              </div>

           </div>
         )
      })}
    </div>
  )
}

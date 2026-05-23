import { useState, useEffect, useMemo } from 'react'
import { useSearchParams, Link } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { Search, X, Trophy, TrendingUp, Star, ArrowRight, ShieldCheck } from 'lucide-react'
import { PRODUCTS, PLATFORMS, formatPrice } from '../data/demoData'

function ScoreBar({ value, max, delay = 0, winner = false }) {
  const percent = Math.min((value / max) * 100, 100)
  return (
    <div className="w-full h-1.5 bg-theme-subtle rounded-full overflow-hidden">
      <motion.div
        initial={{ width: 0 }}
        animate={{ width: `${percent}%` }}
        transition={{ duration: 1.2, delay, ease: [0.22, 1, 0.36, 1] }}
        className={`h-full rounded-full ${winner ? 'bg-[#22c55e]' : 'bg-theme-muted'}`}
      />
    </div>
  )
}

export default function ComparePage() {
  const [searchParams] = useSearchParams()
  
  const id1 = parseInt(searchParams.get('p1'))
  const id2 = parseInt(searchParams.get('p2'))
  
  const initP1 = id1 ? PRODUCTS.find(p => p.id === id1) || PRODUCTS[0] : PRODUCTS[0]
  
  let initP2 = id2 ? PRODUCTS.find(p => p.id === id2) : null;
  // Enforce category similarity at initialization!
  if (initP2 && initP1 && initP2.category !== initP1.category) {
    initP2 = null;
  }
  
  if (!initP2) {
    if (initP1) {
      const similarProducts = PRODUCTS.filter(p => p.category === initP1.category && p.id !== initP1.id);
      similarProducts.sort((a, b) => Math.abs(a.bestPrice - initP1.bestPrice) - Math.abs(b.bestPrice - initP1.bestPrice));
      initP2 = similarProducts[0] || PRODUCTS.find(p => p.id !== initP1.id && p.category === initP1.category);
    }
    if (!initP2) initP2 = PRODUCTS.find(p => p.id !== initP1.id) || PRODUCTS[1];
  }

  const [selected, setSelected] = useState([initP1, initP2])
  
  useEffect(() => {
    // If URL query params update, ensure the categories remain aligned
    let resolvedP2 = initP2;
    if (initP1 && resolvedP2 && initP1.category !== resolvedP2.category) {
      const similar = PRODUCTS.filter(p => p.category === initP1.category && p.id !== initP1.id);
      similar.sort((a, b) => Math.abs(a.bestPrice - initP1.bestPrice) - Math.abs(b.bestPrice - initP1.bestPrice));
      resolvedP2 = similar[0] || PRODUCTS.find(p => p.id !== initP1.id && p.category === initP1.category) || PRODUCTS[1];
    }
    setSelected([initP1, resolvedP2])
  }, [initP1?.id, initP2?.id])

  const [searchSlot, setSearchSlot] = useState(null)
  const [query, setQuery] = useState('')

  const searchResults = useMemo(() => {
    // Find the other product currently selected in the compare slot
    const otherProduct = searchSlot !== null ? selected[1 - searchSlot] : null
    
    let filteredProducts = PRODUCTS
    
    // If the other slot is already occupied, restrict search to the same category!
    if (otherProduct) {
      filteredProducts = PRODUCTS.filter(p => p.category === otherProduct.category)
    }
    
    const q = query.toLowerCase().trim()
    if (!q) {
      // Return first 5 products of the filtered category as suggestions
      return filteredProducts
        .filter(p => !selected.find(s => s?.id === p.id))
        .slice(0, 5)
    }
    
    return filteredProducts
      .filter(p => 
        (p.name.toLowerCase().includes(q) || p.brand.toLowerCase().includes(q)) && 
        !selected.find(s => s?.id === p.id)
      )
      .slice(0, 5)
  }, [query, searchSlot, selected])

  const selectProduct = (p, slot) => {
    const n = [...selected]
    n[slot] = p
    
    // Safety check: if the selected product category differs from the counterpart (should be impossible due to filters, but good as fail-safe),
    // align the counterpart slot automatically
    const otherSlot = 1 - slot
    if (n[otherSlot] && n[otherSlot].category !== p.category) {
      const similar = PRODUCTS.filter(prod => prod.category === p.category && prod.id !== p.id)
      similar.sort((a, b) => Math.abs(a.bestPrice - p.bestPrice) - Math.abs(b.bestPrice - p.bestPrice))
      n[otherSlot] = similar[0] || null
    }
    
    setSelected(n)
    setSearchSlot(null)
    setQuery('')
  }

  const allSpecs = [...new Set(selected.filter(Boolean).flatMap(p => Object.keys(p.specs)))]

  // Compute winner
  const winner = useMemo(() => {
    if (!selected[0] || !selected[1]) return null
    let score0 = 0, score1 = 0
    // Price advantage (lower is better)
    if (selected[0].bestPrice < selected[1].bestPrice) score0 += 2; else if (selected[1].bestPrice < selected[0].bestPrice) score1 += 2;
    // Rating
    if (selected[0].rating > selected[1].rating) score0 += 1.5; else if (selected[1].rating > selected[0].rating) score1 += 1.5;
    // Deal score
    if (selected[0].dealScore > selected[1].dealScore) score0 += 1.5; else if (selected[1].dealScore > selected[0].dealScore) score1 += 1.5;
    // Reviews
    if (selected[0].totalReviews > selected[1].totalReviews) score0 += 1; else if (selected[1].totalReviews > selected[0].totalReviews) score1 += 1;
    if (score0 === score1) return null
    return score0 > score1 ? 0 : 1
  }, [selected])

  return (
    <div className="min-h-screen pt-40 pb-56">
      <div className="w-full max-w-[1536px] mx-auto px-8 md:px-16">
        <div className="mb-40 text-center max-w-4xl mx-auto">
          <span className="text-[0.75rem] font-medium uppercase tracking-[0.15em] block mb-8">Engine</span>
          <h1 className="text-[3rem] sm:text-[4.5rem] lg:text-[5.5rem] font-[var(--font-display)] font-medium leading-[1.05] tracking-tight text-theme-text mb-12">Head-to-Head.</h1>
        </div>

        {/* ─── Product Selection Area ─── */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-px bg-theme-subtle border border-theme-border mb-48">
          {[0, 1].map(slot => {
            const product = selected[slot]
            const isWinner = winner === slot
            const otherProduct = selected[1 - slot]
            return (
              <div key={slot} className={`bg-theme-bg w-full h-full relative p-12 lg:p-24 flex flex-col items-center text-center transition-all duration-500 ${isWinner ? 'ring-1 ring-[#22c55e]/30' : ''}`}>
                {/* Winner badge */}
                {isWinner && selected[0] && selected[1] && (
                  <motion.div 
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="absolute top-6 right-6 z-10 flex items-center gap-1.5 bg-[#22c55e]/10 text-[#22c55e] border border-[#22c55e]/20 px-3 py-1.5 rounded-full"
                  >
                    <Trophy className="w-3 h-3" />
                    <span className="text-[0.6rem] font-bold uppercase tracking-widest">Winner</span>
                  </motion.div>
                )}

                {searchSlot === slot ? (
                  <div className="w-full max-w-md absolute inset-0 bg-theme-elevated z-10 p-12 flex flex-col mx-auto">
                     <div className="flex items-center justify-between mb-12 border-b border-theme-border pb-6">
                        <input type="text" autoFocus value={query} onChange={e=>setQuery(e.target.value)} placeholder={otherProduct ? `SEARCH ${otherProduct.category.toUpperCase()}...` : "SEARCH CATALOG..."} className="w-full bg-transparent outline-none text-[0.875rem] uppercase tracking-widest font-medium" />
                        <button onClick={() => {setSearchSlot(null); setQuery('')}}><X className="w-5 h-5 text-theme-secondary" /></button>
                     </div>
                     <div className="flex-1 overflow-y-auto w-full text-left space-y-4 pr-1">
                        <p className="text-[0.65rem] font-bold text-theme-muted uppercase tracking-[0.15em] mb-4">
                           {query.trim() ? "Search Results" : (otherProduct ? `Suggested ${otherProduct.category}` : "Popular Products")}
                        </p>
                        {searchResults.length > 0 ? (
                          searchResults.map(p => (
                            <button key={p.id} onClick={() => selectProduct(p, slot)} className="w-full flex items-center gap-4 text-left group border-b border-theme-border pb-3 last:border-b-0">
                               <div className="w-12 h-12 bg-white flex items-center justify-center p-1.5 mb-0 rounded-[2px] border border-theme-border"><img src={p.image} alt="" className="mix-blend-multiply max-w-full max-h-full object-contain" /></div>
                               <div className="flex-1 min-w-0">
                                  <p className="text-[0.875rem] font-medium text-theme-text group-hover:text-theme-secondary transition-colors line-clamp-1">{p.name}</p>
                                  <p className="text-[0.75rem] text-theme-muted mt-0.5">{formatPrice(p.bestPrice)}</p>
                                </div>
                            </button>
                          ))
                        ) : (
                          <div className="py-20 text-center">
                            <p className="text-[0.875rem] text-theme-muted italic">No matching products found.</p>
                          </div>
                        )}
                     </div>
                  </div>
                ) : product ? (
                  <>
                     <div className="h-80 mb-16 flex items-center justify-center w-full">
                        <img src={product.image} alt="" className="max-h-full max-w-full object-contain filter drop-shadow-xl" />
                     </div>
                     <span className="text-[0.75rem] font-medium uppercase tracking-[0.15em] mb-4">{product.brand}</span>
                     <h3 className="text-[1.5rem] sm:text-[2rem] lg:text-[2.5rem] font-medium leading-[1.1] tracking-tight text-theme-text mb-6">{product.name}</h3>
                     <p className="text-[2rem] font-medium text-theme-text mb-8">{formatPrice(product.bestPrice)}</p>
                     
                     {/* Quick stats */}
                     <div className="flex items-center gap-6 mb-10">
                       <div className="flex items-center gap-1.5 text-[0.75rem] text-theme-secondary">
                         <Star className="w-3.5 h-3.5 fill-current text-amber-400" />
                         <span>{product.rating}/5</span>
                       </div>
                       <div className="flex items-center gap-1.5 text-[0.75rem] text-theme-secondary">
                         <TrendingUp className="w-3.5 h-3.5 text-[#22c55e]" />
                         <span>Score {product.dealScore}</span>
                       </div>
                     </div>
                     
                     <button onClick={() => setSearchSlot(slot)} className="text-[0.75rem] font-medium uppercase tracking-[0.15em] hover:text-theme-text transition-colors pb-2 mt-2 border-b border-transparent hover:border-theme-text">
                        Change Subject
                     </button>
                  </>
                ) : (
                  <div className="flex-1 flex items-center justify-center py-40">
                     <button onClick={() => setSearchSlot(slot)} className="text-[2rem] font-[var(--font-display)] text-theme-dim hover:text-theme-text transition-colors">
                        + SELECT PRODUCT
                     </button>
                  </div>
                )}
              </div>
            )
          })}
        </div>

        {/* ─── Comparison Data ─── */}
        {selected[0] && selected[1] && (
          <div className="max-w-5xl mx-auto border-t border-theme-border">
             <div className="py-20 flex justify-between items-center px-4">
                <span className="text-[0.75rem] font-medium uppercase tracking-[0.15em] tracking-widest">TECHNICAL SPECIFICATIONS</span>
             </div>

             {/* Dynamic Spec Rows */}
             {allSpecs.map(key => {
                const mapSpecs = [selected[0].specs[key], selected[1].specs[key]]
                return (
                  <div key={key} className="grid grid-cols-12 border-t border-theme-border hover:bg-theme-elevated transition-colors py-12 px-6">
                     <div className="col-span-12 md:col-span-4 mb-4 md:mb-0 flex items-center">
                        <span className="text-[0.875rem] text-theme-secondary">{key}</span>
                     </div>
                     <div className="col-span-6 md:col-span-4 text-center md:text-left text-[1.125rem] font-medium pr-4 border-r border-theme-border md:border-r-0">
                        {mapSpecs[0] !== undefined ? String(mapSpecs[0]) : '—'}
                     </div>
                     <div className="col-span-6 md:col-span-4 text-center md:text-right text-[1.125rem] font-medium pl-4">
                        {mapSpecs[1] !== undefined ? String(mapSpecs[1]) : '—'}
                     </div>
                  </div>
                )
             })}

             {/* Score Comparison with Progress Bars */}
             <div className="py-20 flex justify-between items-center px-4 border-t border-theme-border mt-4">
                <span className="text-[0.75rem] font-medium uppercase tracking-[0.15em] tracking-widest">PERFORMANCE METRICS</span>
             </div>

             {[
               { k: 'Market Price', v: p => p.bestPrice, fmt: v => formatPrice(v), lower: true },
               { k: 'Deal Analysis Score', v: p => p.dealScore, fmt: v => `${v} / 100`, lower: false },
               { k: 'User Satisfaction', v: p => p.rating, fmt: v => `${v} / 5.0`, lower: false },
               { k: 'Total Reviews', v: p => p.totalReviews, fmt: v => v.toLocaleString(), lower: false },
             ].map(row => {
               const v0 = row.v(selected[0])
               const v1 = row.v(selected[1])
               const winner0 = row.lower ? v0 < v1 : v0 > v1
               const winner1 = row.lower ? v1 < v0 : v1 > v0
               const maxVal = Math.max(v0, v1, 1)
               return (
                <div key={row.k} className="border-t border-theme-border hover:bg-theme-elevated transition-colors py-12 px-6">
                   <div className="grid grid-cols-12 items-center">
                     <div className="col-span-12 md:col-span-4 mb-4 md:mb-0 flex items-center">
                        <span className="text-[0.875rem] text-theme-secondary">{row.k}</span>
                     </div>
                     <div className={`col-span-6 md:col-span-4 pr-4 border-r border-theme-border md:border-r-0 ${winner0 ? 'text-[#22c55e]' : 'text-theme-text'}`}>
                        <div className="text-center md:text-left text-[1.125rem] font-medium mb-2">
                          {row.fmt(v0)}
                          {winner0 && <span className="ml-2 text-[0.6rem] uppercase tracking-wider">★</span>}
                        </div>
                        <ScoreBar value={v0} max={maxVal} delay={0.1} winner={winner0} />
                     </div>
                     <div className={`col-span-6 md:col-span-4 pl-4 ${winner1 ? 'text-[#22c55e]' : 'text-theme-text'}`}>
                        <div className="text-center md:text-right text-[1.125rem] font-medium mb-2">
                          {row.fmt(v1)}
                          {winner1 && <span className="ml-2 text-[0.6rem] uppercase tracking-wider">★</span>}
                        </div>
                        <ScoreBar value={v1} max={maxVal} delay={0.2} winner={winner1} />
                     </div>
                   </div>
                </div>
               )
             })}

             {/* Platform Price Comparison */}
             <div className="py-20 flex justify-between items-center px-4 border-t border-theme-border mt-4">
                <span className="text-[0.75rem] font-medium uppercase tracking-[0.15em] tracking-widest">CROSS-PLATFORM PRICING</span>
             </div>

             {(() => {
               const allPlatforms = [...new Set([
                 ...selected[0].prices.map(p => p.platform),
                 ...selected[1].prices.map(p => p.platform)
               ])]
               return allPlatforms.map(platform => {
                 const p0 = selected[0].prices.find(p => p.platform === platform)
                 const p1 = selected[1].prices.find(p => p.platform === platform)
                 return (
                   <div key={platform} className="grid grid-cols-12 border-t border-theme-border hover:bg-theme-elevated transition-colors py-8 px-6 items-center">
                     <div className="col-span-12 md:col-span-4 mb-3 md:mb-0 flex items-center gap-3">
                       <span className="text-[1rem]">{PLATFORMS[platform]?.icon}</span>
                       <span className="text-[0.875rem] font-medium text-theme-text">{PLATFORMS[platform]?.name || platform}</span>
                     </div>
                     <div className="col-span-6 md:col-span-4 text-center md:text-left text-[1rem] pr-4 border-r border-theme-border md:border-r-0">
                       {p0 ? <span className="font-medium">{formatPrice(p0.price)}</span> : <span className="text-theme-dim">—</span>}
                     </div>
                     <div className="col-span-6 md:col-span-4 text-center md:text-right text-[1rem] pl-4">
                       {p1 ? <span className="font-medium">{formatPrice(p1.price)}</span> : <span className="text-theme-dim">—</span>}
                     </div>
                   </div>
                 )
               })
             })()}

             {/* Verdict Block */}
             <div className="border-t border-theme-border py-24 px-6">
                <div className="grid grid-cols-12 items-start">
                  <div className="col-span-12 md:col-span-4 mb-8 md:mb-0">
                     <span className="text-[0.75rem] font-medium uppercase tracking-[0.15em]">Algorithmic Synthesis</span>
                  </div>
                  <div className="col-span-12 md:col-span-8">
                     {winner !== null ? (
                       <div>
                         <div className="flex items-center gap-3 mb-6">
                           <ShieldCheck className="w-5 h-5 text-[#22c55e]" />
                           <span className="text-[0.75rem] font-bold uppercase tracking-[0.15em] text-[#22c55e]">Verdict Determined</span>
                         </div>
                         <p className="text-[1.125rem] sm:text-[1.25rem] leading-[1.6] tracking-tight text-theme-secondary">
                           Analyzing technical capabilities against market value, 
                           <span className="text-theme-text font-medium mx-1">{selected[winner].name}</span> 
                           presents superior quantitative metrics with a deal score of <span className="text-[#22c55e] font-medium">{selected[winner].dealScore}/100</span> and 
                           user satisfaction of <span className="text-[#22c55e] font-medium">{selected[winner].rating}/5.0</span>.
                           {selected[winner].bestPrice < selected[winner === 0 ? 1 : 0].bestPrice && 
                             <> It also offers a <span className="text-[#22c55e] font-medium">{formatPrice(selected[winner === 0 ? 1 : 0].bestPrice - selected[winner].bestPrice)}</span> price advantage.</>
                           }
                         </p>
                         <Link to={`/product/${selected[winner].id}`} className="inline-flex items-center gap-2 mt-8 text-[0.75rem] font-medium uppercase tracking-[0.15em] text-theme-text hover:text-[#22c55e] transition-colors border-b border-transparent hover:border-[#22c55e] pb-1">
                           View Winner Details <ArrowRight className="w-3.5 h-3.5" />
                         </Link>
                       </div>
                     ) : (
                       <p className="text-[1.125rem] sm:text-[1.25rem] leading-[1.6] tracking-tight text-theme-secondary">
                         Both products demonstrate equivalent quantitative metrics. The optimal choice depends on subjective user preferences and specific use-case requirements. Refer to raw specifications for binary differentiation.
                       </p>
                     )}
                  </div>
                </div>
             </div>
          </div>
        )}
      </div>
    </div>
  )
}

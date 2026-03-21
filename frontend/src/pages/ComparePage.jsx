import { useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { Search, X } from 'lucide-react'
import { PRODUCTS } from '../data/demoData'

export default function ComparePage() {
  const [searchParams] = useSearchParams()
  
  const id1 = parseInt(searchParams.get('p1'))
  const id2 = parseInt(searchParams.get('p2'))
  
  const initP1 = id1 ? PRODUCTS.find(p => p.id === id1) : PRODUCTS[0]
  const initP2 = id2 ? PRODUCTS.find(p => p.id === id2) : PRODUCTS[1]

  const [selected, setSelected] = useState([initP1, initP2])
  const [searchSlot, setSearchSlot] = useState(null)
  const [query, setQuery] = useState('')

  const searchResults = query ? PRODUCTS.filter(p => p.name.toLowerCase().includes(query.toLowerCase()) && !selected.find(s => s?.id === p.id)).slice(0, 5) : []

  const selectProduct = (p, slot) => { const n = [...selected]; n[slot] = p; setSelected(n); setSearchSlot(null); setQuery('') }

  const allSpecs = [...new Set(selected.filter(Boolean).flatMap(p => Object.keys(p.specs)))]

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
            return (
              <div key={slot} className="bg-theme-bg w-full h-full relative p-12 lg:p-24 flex flex-col items-center text-center">
                {searchSlot === slot ? (
                  <div className="w-full max-w-md absolute inset-0 bg-theme-elevated z-10 p-12 flex flex-col mx-auto">
                     <div className="flex items-center justify-between mb-12 border-b border-theme-border pb-6">
                        <input type="text" autoFocus value={query} onChange={e=>setQuery(e.target.value)} placeholder="SEARCH CATALOG..." className="w-full bg-transparent outline-none text-[0.875rem] uppercase tracking-widest font-medium" />
                        <button onClick={() => {setSearchSlot(null); setQuery('')}}><X className="w-5 h-5 text-theme-secondary" /></button>
                     </div>
                     <div className="flex-1 overflow-y-auto w-full text-left space-y-4">
                        {searchResults.map(p => (
                          <button key={p.id} onClick={() => selectProduct(p, slot)} className="w-full flex items-center gap-4 text-left group">
                             <div className="w-12 h-12 bg-theme-text flex items-center justify-center p-2 mb-0"><img src={p.image} alt="" className="mix-blend-multiply" /></div>
                             <div>
                                <p className="text-[0.875rem] font-medium text-theme-text group-hover:text-theme-secondary transition-colors">{p.name}</p>
                                <p className="text-[0.75rem] text-theme-muted">${p.bestPrice}</p>
                             </div>
                          </button>
                        ))}
                     </div>
                  </div>
                ) : product ? (
                  <>
                     <div className="h-80 mb-16 flex items-center justify-center mix-blend-screen w-full">
                        <img src={product.image} alt="" className="max-h-full max-w-full object-contain filter drop-shadow-xl" />
                     </div>
                     <span className="text-[0.75rem] font-medium uppercase tracking-[0.15em] mb-4">{product.brand}</span>
                     <h3 className="text-[2rem] sm:text-[3rem] lg:text-[3.5rem] font-medium leading-[1.1] tracking-tight text-theme-text text-[2rem] mb-6">{product.name}</h3>
                     <p className="text-[2rem] font-medium text-theme-text mb-16">${product.bestPrice}</p>
                     
                     <button onClick={() => setSearchSlot(slot)} className="text-[0.75rem] font-medium uppercase tracking-[0.15em] hover:text-theme-text transition-colors pb-2 mt-8 border-b border-transparent hover:border-theme-text">
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

             {/* Metrics Rows */}
             {[
               { k: 'Market Price', v: p => `$${p.bestPrice}` },
               { k: 'Deal Analysis Score', v: p => `${p.dealScore} / 100` },
               { k: 'User Satisfaction', v: p => `${p.rating} / 5.0` },
             ].map(row => (
               <div key={row.k} className="grid grid-cols-12 border-t border-theme-border hover:bg-theme-elevated transition-colors py-12 px-6">
                  <div className="col-span-12 md:col-span-4 mb-4 md:mb-0 flex items-center">
                     <span className="text-[0.875rem] text-theme-secondary">{row.k}</span>
                  </div>
                  <div className="col-span-6 md:col-span-4 text-center md:text-left text-[1.125rem] font-medium pr-4 border-r border-theme-border md:border-r-0">
                     {row.v(selected[0])}
                  </div>
                  <div className="col-span-6 md:col-span-4 text-center md:text-right text-[1.125rem] font-medium pl-4">
                     {row.v(selected[1])}
                  </div>
               </div>
             ))}

             {/* Verdict Block */}
             <div className="grid grid-cols-12 border-t border-theme-border py-24 px-6 items-center">
                 <div className="col-span-12 md:col-span-4 mb-8 md:mb-0">
                    <span className="text-[0.75rem] font-medium uppercase tracking-[0.15em]">Algorithmic Synthesis</span>
                 </div>
                 <div className="col-span-12 md:col-span-8">
                    <p className="text-[1.125rem] sm:text-[1.25rem] leading-[1.6] tracking-tight text-theme-secondary">
                      Analyzing technical capabilities against market value, 
                      <span className="text-theme-text mx-1">{selected[0].dealScore > selected[1].dealScore ? selected[0].name : selected[1].name}</span> 
                      presents superior quantitative metrics. However, subjective aesthetic variables depend entirely on end-user constraints. Refer to raw specs for binary differentiation.
                    </p>
                 </div>
             </div>
          </div>
        )}
      </div>
    </div>
  )
}

import { useState, useRef, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { ArrowRight } from 'lucide-react'
import { PRODUCTS, PLATFORMS } from '../data/demoData'

const SUGGESTIONS = ['Best headphones for mixing', 'Minimalist laptop under $1500', 'Top rated wireless audio', 'Nike vs Adidas durability']

function findRecs(query) {
  const q = query.toLowerCase()
  let r = [...PRODUCTS]
  
  const bm = q.match(/under\s*\$?(\d+)/i) || q.match(/below\s*\$?(\d+)/i)
  if (bm) r = r.filter(p => p.bestPrice <= parseInt(bm[1]))
  
  const categories = [...new Set(PRODUCTS.map(p => p.category.toLowerCase()))]
  let targetCategory = null

  // 1. Direct Category Name Match
  for (const cat of categories) {
    if (q.includes(cat) || (cat.endsWith('s') && q.includes(cat.slice(0, -1)))) {
      targetCategory = cat; break
    }
  }
  
  // 2. High-Accuracy NLP Keyword Mapping (Bounded to prevent overlaps)
  if (!targetCategory) {
    if (q.match(/\b(phone|smartphone|mobile|cell|iphone|galaxy)\b/i)) targetCategory = 'smartphones'
    else if (q.match(/\b(laptop|macbook|pc|computer|desktop)\b/i)) targetCategory = 'laptops'
    else if (q.match(/\b(shoe|sneaker|kicks|footwear|runner)\b/i)) targetCategory = 'shoes'
    else if (q.match(/\b(headphone|earbud|audio|music|sound|airpods)\b/i)) targetCategory = 'headphones'
    else if (q.match(/\b(tv|television|oled|screen|display)\b/i)) targetCategory = 'electronics'
    else if (q.match(/\b(watch|luxury|rolex|timepiece)\b/i)) targetCategory = 'premium products'
    else if (q.match(/\b(vacuum|cleaner|appliance|home)\b/i)) targetCategory = 'home appliance'
    else if (q.match(/\b(shirt|dress|jeans|pants|wear|apparel|clothes)\b/i)) targetCategory = 'mens wear'
    else if (q.match(/\b(toothpaste|brush|essential|daily)\b/i)) targetCategory = 'everyday essential'
  }

  // 3. Entity Resolution: Check if brand or exact name was explicitly requested
  const exactProducts = r.filter(p => q.includes(p.brand.toLowerCase()) || q.includes(p.name.toLowerCase().split(' ')[0]))
  
  if (exactProducts.length > 0) {
      r = exactProducts
  } else if (targetCategory) {
      r = r.filter(p => p.category.toLowerCase() === targetCategory)
  }

  r.sort((a, b) => (b.rating * b.dealScore) - (a.rating * a.dealScore))
  return r.slice(0, 3)
}

function analyzeDeal(product) {
  if (!product || !product.prices || product.prices.length === 0) return ''
  const prices = [...product.prices].sort((a, b) => a.price - b.price)
  const best = prices[0]
  const worst = prices[prices.length - 1]
  const saved = (worst.price - best.price).toFixed(2)
  const percent = Math.round((saved / worst.price) * 100)
  
  let r = `\n\nAI DEAL SCANNER:`
  r += `\nAnalyzed ${prices.length} distinct merchant platforms and established arbitrage.`
  r += `\n- BEST PRICE: $${best.price} via ${PLATFORMS[best.platform]?.name || best.platform.toUpperCase()}`
  if (prices.length > 1) {
    r += `\n- WORST PRICE: $${worst.price} via ${PLATFORMS[worst.platform]?.name || worst.platform.toUpperCase()}`
    r += `\n- OPTIMAL SAVINGS: $${saved} (${percent}% differential)`
  }
  return r
}

function genResp(query, products) {
  if (!products.length) return `Query unrecognized. No hardware specifications found matching "${query}". Please adjust parameters.`
  const top = products[0]
  let r = `Analysis complete for: "${query}".\n\n`
  r += `PRIMARY RECOMMENDATION:\n${top.name}\nScore: ${top.dealScore}/100 | Verification: Authentic`
  r += analyzeDeal(top)
  if (products.length > 1) {
     r += `\n\nMARKET ALTERNATIVES:`
     products.slice(1).map(p => {
        r += `\n- ${p.name} ($${p.bestPrice})`
     })
  }
  return r
}

export default function AIAdvisorPage() {
  const [messages, setMessages] = useState(() => {
    const interest = localStorage.getItem('bb_user_interest')
    let content = "SYSTEM ONLINE. Algorithm ready for queries. State requirements, budget, or specifications."
    let products = []
    
    if (interest) {
      const categoryProducts = [...PRODUCTS].filter(p => p.category.toLowerCase() === interest.toLowerCase()).sort((a,b) => b.dealScore - a.dealScore)
      if (categoryProducts.length > 0) {
         const top = categoryProducts[0]
         products = [top]
         content = `SYSTEM_ONLINE\n\nI noticed you were recently exploring ${interest.toUpperCase()}.\nI immediately ran a background scan across all known platforms for this category.\n\nTOP NEGOTIATED DEAL: ${top.name}`
         content += analyzeDeal(top)
         content += `\n\nWould you like to lock this deal in immediately, or should we compare other alternatives?`
      } else {
         content = `SYSTEM_ONLINE\n\nI noticed you were recently exploring ${interest.toUpperCase()}. Would you like me to run a deep-dive benchmark on the top-rated models in that tier, hunt for hidden clearance deals, or are we shifting focus to a new category today?`
      }
    }
    return [{ role: 'assistant', content, products }]
  })
  const [input, setInput] = useState('')
  const [typing, setTyping] = useState(false)
  const scrollContainerRef = useRef(null)

  useEffect(() => { 
     if (scrollContainerRef.current) {
        scrollContainerRef.current.scrollTo({
           top: scrollContainerRef.current.scrollHeight,
           behavior: 'smooth'
        })
     }
  }, [messages, typing])

  const send = async (text = input) => {
    if (!text.trim()) return
    setMessages(p => [...p, { role: 'user', content: `> ${text.trim().toUpperCase()}` }])
    setInput(''); setTyping(true)
    await new Promise(r => setTimeout(r, 1200 + Math.random() * 800))
    const products = findRecs(text)
    setMessages(p => [...p, { role: 'assistant', content: genResp(text, products), products }])
    setTyping(false)
  }

  return (
    <div className="min-h-screen pt-40 pb-56 flex flex-col items-center">
      <div className="w-full max-w-4xl flex flex-col h-[80vh] border border-theme-border bg-theme-bg">
         
         <div className="border-b border-theme-border p-6 lg:px-12 flex justify-between items-center bg-theme-elevated">
            <span className="text-[0.75rem] font-medium uppercase tracking-[0.15em] text-theme-text tracking-widest">Brand Battle Intelligence Terminal</span>
            <span className="text-[0.65rem] text-theme-dim uppercase tracking-widest whitespace-nowrap">Status: Active</span>
         </div>

         <div ref={scrollContainerRef} className="flex-1 overflow-y-auto p-10 lg:p-16 space-y-16 font-[var(--font-mono)] text-[0.875rem] leading-relaxed relative">
            <AnimatePresence>
              {messages.map((msg, i) => (
                <motion.div key={i} initial={{ opacity: 0 }} animate={{ opacity: 1 }} className={`w-full ${msg.role === 'user' ? 'text-theme-secondary' : 'text-theme-text'}`}>
                   {msg.content.split('\n').map((line, j) => (
                      <p key={j} className="min-h-[1.5em] font-mono">{line}</p>
                   ))}
                   
                   {msg.products?.length > 0 && (
                      <div className="mt-12 grid grid-cols-1 sm:grid-cols-3 gap-px bg-theme-subtle border border-theme-border">
                         {msg.products.map((p, pIdx) => (
                            <Link key={p.id} to={`/product/${p.id}`} className="bg-theme-bg p-6 group hover:bg-theme-elevated transition-colors relative overflow-hidden">
                               
                               {pIdx === 0 && (
                                  <div className="absolute top-4 left-4 z-10">
                                     <div className="bg-[#22c55e] text-black text-[0.55rem] font-bold tracking-widest uppercase px-3 py-1 scale-90 sm:scale-100 origin-top-left flex items-center gap-1 shadow-[0_0_15px_rgba(34,197,94,0.3)]">
                                        ★ Best Product For You
                                     </div>
                                  </div>
                               )}
                               
                               <div className="aspect-square bg-theme-text flex items-center justify-center p-6 mb-6">
                                  <img src={p.image} className="max-w-full max-h-full mix-blend-multiply group-hover:scale-110 transition-transform duration-500 relative z-0" />
                               </div>
                               <p className="text-[0.75rem] uppercase tracking-wider text-theme-muted truncate mb-1">{p.brand}</p>
                               <p className="font-medium text-theme-text text-[0.875rem] truncate mb-2">{p.name}</p>
                               <div className="flex justify-between items-center text-[0.75rem]">
                                  <span className="text-theme-text">${p.bestPrice}</span>
                                  <ArrowRight className="w-3 h-3 text-theme-dim group-hover:text-theme-text transition-colors" />
                               </div>
                            </Link>
                         ))}
                      </div>
                   )}
                </motion.div>
              ))}
              {typing && (
                 <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex gap-2 items-center text-theme-muted opacity-50 font-mono">
                    <span className="w-2 h-4 bg-theme-text animate-pulse"></span> PROCESSING
                 </motion.div>
              )}
            </AnimatePresence>
         </div>

         <div className="border-t border-theme-border p-6 lg:px-12 bg-theme-bg">
            <form onSubmit={e => { e.preventDefault(); send() }} className="flex items-center gap-6">
               <span className="text-theme-secondary font-mono">_</span>
               <input 
                  type="text" 
                  value={input} 
                  onChange={e => setInput(e.target.value)}
                  placeholder="INPUT QUERY..."
                  className="flex-1 bg-transparent text-theme-text placeholder:text-theme-dim font-mono text-[0.875rem] focus:outline-none uppercase tracking-widest"
                  autoFocus
               />
               <button type="submit" disabled={!input.trim()} className="text-[0.875rem] uppercase tracking-widest font-mono text-theme-secondary hover:text-theme-text disabled:opacity-20 disabled:cursor-not-allowed transition-colors">
                  Submit
               </button>
            </form>
         </div>
      </div>

      <div className="w-full max-w-3xl mt-8 flex gap-4 overflow-x-auto pb-4 hide-scrollbar">
         {SUGGESTIONS.map((s, i) => (
            <button key={i} onClick={() => send(s)} className="shrink-0 px-4 py-2 border border-theme-border text-[0.65rem] uppercase tracking-widest text-theme-muted hover:text-theme-text hover:border-theme-text transition-colors">
               {s}
            </button>
         ))}
      </div>
    </div>
  )
}

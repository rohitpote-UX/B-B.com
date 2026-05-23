import { useState, useRef, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { ArrowRight, Zap, Bot, User } from 'lucide-react'
import { PRODUCTS, PLATFORMS, formatPrice } from '../data/demoData'

const SUGGESTIONS = ['Best headphones for mixing', 'Minimalist laptop under $1500', 'Top rated wireless audio', 'Nike vs Adidas durability', 'Budget smartphone under $300']

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
  
  let r = `\n\n⚡ AI DEAL SCANNER:`
  r += `\nAnalyzed ${prices.length} distinct merchant platforms and established arbitrage.`
  r += `\n→ BEST PRICE: $${best.price} (₹${Math.round(best.price * 84).toLocaleString()}) via ${PLATFORMS[best.platform]?.name || best.platform.toUpperCase()}`
  if (prices.length > 1) {
    r += `\n→ WORST PRICE: $${worst.price} (₹${Math.round(worst.price * 84).toLocaleString()}) via ${PLATFORMS[worst.platform]?.name || worst.platform.toUpperCase()}`
    r += `\n→ OPTIMAL SAVINGS: $${saved} (₹${Math.round(saved * 84).toLocaleString()}) (${percent}% differential)`
  }
  return r
}

function genResp(query, products) {
  if (!products.length) return `⚠ Query unrecognized. No specifications found matching "${query}". Please adjust parameters.`
  const top = products[0]
  let r = `Analysis complete for: "${query}".\n\n`
  r += `★ PRIMARY RECOMMENDATION:\n${top.name}\nScore: ${top.dealScore}/100 | Rating: ${top.rating}/5.0 | Verification: Authentic`
  r += analyzeDeal(top)
  if (products.length > 1) {
     r += `\n\n◆ MARKET ALTERNATIVES:`
     products.slice(1).map(p => {
        r += `\n  → ${p.name} ($${p.bestPrice} / ₹${Math.round(p.bestPrice * 84).toLocaleString()}) — Score: ${p.dealScore}/100`
     })
  }
  return r
}

export default function AIAdvisorPage() {
  const [messages, setMessages] = useState(() => {
    const interest = localStorage.getItem('bb_user_interest')
    let content = "◉ SYSTEM ONLINE\n\nAlgorithm ready for queries. State requirements, budget, or specifications.\n\nTry asking me:\n→ \"Best laptop under $1000\"\n→ \"Compare headphones for music production\"\n→ \"Budget smartphone with great camera\""
    let products = []
    
    if (interest) {
      const categoryProducts = [...PRODUCTS].filter(p => p.category.toLowerCase() === interest.toLowerCase()).sort((a,b) => b.dealScore - a.dealScore)
      if (categoryProducts.length > 0) {
         const top = categoryProducts[0]
         products = [top]
         content = `◉ SYSTEM ONLINE\n\nI noticed you were recently exploring ${interest.toUpperCase()}.\nI immediately ran a background scan across all known platforms for this category.\n\n★ TOP NEGOTIATED DEAL: ${top.name}`
         content += analyzeDeal(top)
         content += `\n\nWould you like to lock this deal in immediately, or should we compare other alternatives?`
      } else {
         content = `◉ SYSTEM ONLINE\n\nI noticed you were recently exploring ${interest.toUpperCase()}. Would you like me to run a deep-dive benchmark on the top-rated models in that tier, hunt for hidden clearance deals, or are we shifting focus to a new category today?`
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
    setMessages(p => [...p, { role: 'user', content: text.trim() }])
    setInput(''); setTyping(true)
    await new Promise(r => setTimeout(r, 1200 + Math.random() * 800))
    const products = findRecs(text)
    setMessages(p => [...p, { role: 'assistant', content: genResp(text, products), products }])
    setTyping(false)
  }

  return (
    <div className="min-h-screen pt-32 pb-40 flex flex-col items-center px-4">
      
      {/* Title */}
      <div className="w-full max-w-4xl mb-8">
        <span className="text-[0.75rem] font-medium uppercase tracking-[0.15em] block mb-4 text-theme-muted">Intelligence</span>
        <h1 className="text-[2rem] sm:text-[3rem] font-[var(--font-display)] font-medium leading-[1.1] tracking-tight text-theme-text mb-4">AI Advisor.</h1>
        <p className="text-[1rem] text-theme-secondary max-w-xl">Ask me anything about products, deals, or comparisons. I'll analyze real market data to give you the best recommendation.</p>
      </div>

      <div className="w-full max-w-4xl flex flex-col h-[70vh] border border-theme-border bg-theme-bg rounded-sm overflow-hidden">
         
         <div className="border-b border-theme-border px-6 py-4 lg:px-10 flex justify-between items-center bg-theme-elevated">
            <div className="flex items-center gap-3">
              <div className="w-2 h-2 rounded-full bg-[#22c55e] animate-pulse" />
              <span className="text-[0.7rem] font-medium uppercase tracking-[0.15em] text-theme-text">Brand Battle Intelligence Terminal</span>
            </div>
            <span className="text-[0.6rem] text-theme-muted uppercase tracking-widest whitespace-nowrap">v2.0 · Active</span>
         </div>

         <div ref={scrollContainerRef} className="flex-1 overflow-y-auto p-6 lg:p-10 space-y-8 relative">
            <AnimatePresence>
              {messages.map((msg, i) => (
                <motion.div 
                  key={i} 
                  initial={{ opacity: 0, y: 10 }} 
                  animate={{ opacity: 1, y: 0 }} 
                  transition={{ duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
                  className={`flex gap-4 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                   {msg.role === 'assistant' && (
                     <div className="w-8 h-8 rounded-full bg-theme-elevated border border-theme-border flex items-center justify-center shrink-0 mt-1">
                       <Bot className="w-4 h-4 text-[#22c55e]" />
                     </div>
                   )}
                   
                   <div className={`max-w-[85%] ${msg.role === 'user' ? 'order-1' : ''}`}>
                     <div className={`px-5 py-4 rounded-lg ${
                       msg.role === 'user' 
                         ? 'bg-theme-text text-theme-bg ml-auto' 
                         : 'bg-theme-elevated border border-theme-border text-theme-text'
                     }`}>
                       {msg.content.split('\n').map((line, j) => (
                          <p key={j} className={`min-h-[1.2em] text-[0.85rem] leading-relaxed font-[var(--font-mono,monospace)] ${
                            line.startsWith('★') || line.startsWith('◆') || line.startsWith('◉') || line.startsWith('⚡') || line.startsWith('⚠')
                              ? 'font-semibold mt-1' 
                              : line.startsWith('→') 
                                ? 'pl-2 text-inherit opacity-80' 
                                : ''
                          }`}>{line || '\u00A0'}</p>
                       ))}
                     </div>
                     
                     {msg.products?.length > 0 && (
                        <div className="mt-4 grid grid-cols-1 sm:grid-cols-3 gap-2">
                           {msg.products.map((p, pIdx) => (
                              <Link key={p.id} to={`/product/${p.id}`} className="bg-theme-elevated border border-theme-border rounded-lg p-4 group hover:border-theme-strong transition-all duration-300 relative overflow-hidden">
                                 
                                 {pIdx === 0 && (
                                    <div className="absolute top-3 left-3 z-10">
                                       <div className="bg-[#22c55e] text-black text-[0.5rem] font-bold tracking-widest uppercase px-2.5 py-1 rounded-full flex items-center gap-1">
                                          ★ Best Pick
                                       </div>
                                    </div>
                                 )}
                                 
                                 <div className="aspect-square bg-theme-bg rounded-md flex items-center justify-center p-4 mb-3 overflow-hidden">
                                    <img src={p.image} className="max-w-full max-h-full object-contain group-hover:scale-110 transition-transform duration-500" />
                                 </div>
                                 <p className="text-[0.65rem] uppercase tracking-wider text-theme-muted truncate mb-0.5">{p.brand}</p>
                                 <p className="font-medium text-theme-text text-[0.8rem] truncate mb-2">{p.name}</p>
                                 <div className="flex justify-between items-center text-[0.75rem]">
                                    <span className="text-theme-text font-medium">{formatPrice(p.bestPrice)}</span>
                                    <ArrowRight className="w-3 h-3 text-theme-dim group-hover:text-theme-text transition-colors" />
                                 </div>
                              </Link>
                           ))}
                        </div>
                     )}
                   </div>

                   {msg.role === 'user' && (
                     <div className="w-8 h-8 rounded-full bg-theme-text flex items-center justify-center shrink-0 mt-1 order-2">
                       <User className="w-4 h-4 text-theme-bg" />
                     </div>
                   )}
                </motion.div>
              ))}
              {typing && (
                 <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex gap-4 items-start">
                    <div className="w-8 h-8 rounded-full bg-theme-elevated border border-theme-border flex items-center justify-center shrink-0">
                      <Bot className="w-4 h-4 text-[#22c55e]" />
                    </div>
                    <div className="bg-theme-elevated border border-theme-border rounded-lg px-5 py-4 flex items-center gap-2.5">
                       <span className="w-2 h-2 rounded-full bg-[#22c55e] animate-pulse" />
                       <span className="w-2 h-2 rounded-full bg-[#22c55e] animate-pulse" style={{ animationDelay: '0.2s' }} />
                       <span className="w-2 h-2 rounded-full bg-[#22c55e] animate-pulse" style={{ animationDelay: '0.4s' }} />
                       <span className="text-[0.75rem] text-theme-muted uppercase tracking-widest ml-2">Processing</span>
                    </div>
                 </motion.div>
              )}
            </AnimatePresence>
         </div>

         <div className="border-t border-theme-border p-4 lg:px-10 bg-theme-bg">
            <form onSubmit={e => { e.preventDefault(); send() }} className="flex items-center gap-4 bg-theme-elevated border border-theme-border rounded-lg px-4 py-3 focus-within:border-theme-strong transition-colors">
               <Zap className="w-4 h-4 text-[#22c55e] shrink-0" />
               <input 
                  type="text" 
                  value={input} 
                  onChange={e => setInput(e.target.value)}
                  placeholder="Ask about any product, deal, or comparison..."
                  className="flex-1 bg-transparent text-theme-text placeholder:text-theme-dim text-[0.875rem] focus:outline-none"
                  autoFocus
               />
               <button type="submit" disabled={!input.trim()} className="text-[0.75rem] uppercase tracking-widest font-medium text-theme-muted hover:text-theme-text disabled:opacity-20 disabled:cursor-not-allowed transition-colors px-3 py-1.5 border border-theme-border rounded-md hover:border-theme-strong">
                  Send
               </button>
            </form>
         </div>
      </div>

      <div className="w-full max-w-4xl mt-5 flex gap-2.5 overflow-x-auto pb-4 hide-scrollbar">
         {SUGGESTIONS.map((s, i) => (
            <button key={i} onClick={() => send(s)} className="shrink-0 px-4 py-2 border border-theme-border text-[0.65rem] uppercase tracking-widest text-theme-muted hover:text-theme-text hover:border-theme-text transition-colors rounded-full bg-theme-bg hover:bg-theme-elevated">
               {s}
            </button>
         ))}
      </div>
    </div>
  )
}

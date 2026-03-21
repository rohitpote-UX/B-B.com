import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Settings, Heart, Cpu, ArrowRight } from 'lucide-react'
import { PRODUCTS } from '../data/demoData'

export default function ProfilePage() {
  const [interest, setInterest] = useState('None')
  const [savedProducts, setSavedProducts] = useState([])

  useEffect(() => {
    // Load Behavioral Algorithms
    setInterest(localStorage.getItem('bb_user_interest') || 'None')
    try {
      const savedIds = JSON.parse(localStorage.getItem('bb_liked_products') || '[]')
      // Map IDs back to full products
      const products = PRODUCTS.filter(p => savedIds.includes(p.uniqueId) || savedIds.includes(p.id) || savedIds.includes(p.id.toString()))
      setSavedProducts(products)
    } catch { setSavedProducts([]) }
  }, [])

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
                  <div className="text-3xl font-[var(--font-display)]">4</div>
               </div>
               <div>
                  <div className="text-[0.65rem] uppercase tracking-widest text-theme-muted mb-2 font-mono">Total Savings</div>
                  <div className="text-3xl font-[var(--font-display)] text-[#22c55e]">$420</div>
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

         {/* Saved Arsenal */}
         <div className="md:col-span-3 bg-theme-bg border border-theme-border rounded-[2rem] p-8 md:p-12 mt-2">
            <div className="flex items-center justify-between mb-8">
               <div className="flex items-center gap-3">
                  <Heart className="w-5 h-5 text-theme-text fill-theme-text" />
                  <span className="text-[0.65rem] uppercase tracking-widest font-mono text-theme-text">Your Saved Arsenal</span>
               </div>
               <Link to="/discover" className="text-[0.75rem] uppercase tracking-widest text-theme-secondary hover:text-theme-text transition-colors flex items-center gap-2">
                  Discover More <ArrowRight className="w-3 h-3" />
               </Link>
            </div>
            
            {savedProducts.length > 0 ? (
               <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
                  {savedProducts.map((p, idx) => (
                     <Link key={idx} to={`/product/${p.id}`} className="block group">
                        <div className="aspect-[4/3] bg-theme-elevated p-8 mb-4 border border-theme-border flex items-center justify-center overflow-hidden rounded-xl group-hover:border-theme-text/50 transition-colors">
                           <img src={p.image} className="max-w-full max-h-full object-contain mix-blend-multiply group-hover:scale-110 transition-transform duration-700 ease-out" />
                        </div>
                        <div className="flex justify-between items-start">
                           <div>
                              <p className="text-[0.65rem] font-bold uppercase tracking-widest text-theme-muted mb-1">{p.brand}</p>
                              <p className="font-medium text-[0.875rem] text-theme-text truncate max-w-[150px]">{p.name}</p>
                           </div>
                           <p className="text-[0.875rem] font-[var(--font-display)]">${p.bestPrice}</p>
                        </div>
                     </Link>
                  ))}
               </div>
            ) : (
               <div className="py-24 flex flex-col items-center justify-center text-center border border-dashed border-theme-border/50 rounded-xl bg-theme-elevated/20">
                  <p className="text-theme-text font-medium mb-2">No hardware saved yet.</p>
                  <p className="text-[0.875rem] text-theme-secondary mb-6 max-w-sm">Tap the heart icon on any product in the Discover feed to push it to your personal arsenal.</p>
                  <Link to="/discover" className="px-6 py-2.5 bg-theme-text text-theme-bg text-[0.65rem] font-bold uppercase tracking-widest rounded-[2px] transition-transform hover:scale-[1.05]">
                     Launch Discover
                  </Link>
               </div>
            )}
         </div>

      </div>
    </motion.div>
  )
}

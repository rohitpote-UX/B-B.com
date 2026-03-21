import { useState, useMemo } from 'react'
import { useParams, Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { ArrowLeft, ArrowUpRight } from 'lucide-react'
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'
import { PRODUCTS, PLATFORMS, generatePriceHistory } from '../data/demoData'

export default function ProductDetailPage() {
  const { id } = useParams()
  const product = PRODUCTS.find(p => p.id === parseInt(id)) || PRODUCTS[0]
  const priceHistory = useMemo(() => generatePriceHistory(product.bestPrice), [product])
  
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
                className="max-w-full max-h-full object-contain filter drop-shadow-2xl mix-blend-screen group-hover:scale-110 transition-transform duration-[1.5s]" 
              />
           </div>

           {/* Details */}
           <div className="col-span-12 lg:col-span-5 lg:col-start-8 py-16 lg:py-0">
              <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.8, delay: 0.2 }}>
                 <span className="text-[0.75rem] font-medium uppercase tracking-[0.15em] block mb-8">{product.brand} · {product.category}</span>
                 <h1 className="text-[3rem] sm:text-[4.5rem] lg:text-[5.5rem] font-[var(--font-display)] font-medium leading-[1.05] tracking-tight text-theme-text mb-12 tracking-tight leading-none">{product.name}</h1>
                 
                 <div className="flex items-baseline gap-6 mb-16 pb-16 border-b border-theme-border">
                    <span className="text-[2.5rem] font-medium text-theme-text">${product.bestPrice}</span>
                    <span className="text-[1.25rem] text-theme-muted line-through">${product.originalPrice}</span>
                 </div>

                 <p className="text-[1.125rem] sm:text-[1.25rem] leading-[1.6] tracking-tight text-theme-secondary mb-20 leading-relaxed">
                   {product.description}
                 </p>

                 <div className="flex flex-col sm:flex-row gap-4">
                    <button className="inline-flex items-center justify-center px-10 py-5 bg-transparent border border-theme-text text-theme-text text-[0.875rem] font-medium tracking-wide transition-all duration-300 rounded-[2px] hover:bg-theme-text hover:text-theme-bg w-full sm:w-auto px-12">
                       Purchase Now
                    </button>
                    <button className="inline-flex items-center justify-center px-10 py-5 bg-transparent border border-theme-border text-theme-text text-[0.875rem] font-medium tracking-wide transition-all duration-300 rounded-[2px] hover:border-theme-text w-full sm:w-auto flex items-center gap-2">
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
                                <span className="block text-[1.125rem] font-medium">${p.price}</span>
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
    </div>
  )
}

'use client'

import { useState } from 'react'
import Link from 'next/link'
import { motion } from 'framer-motion'
import { ArrowRight } from 'lucide-react'
import { DEALS, PLATFORMS, formatPrice } from '@/data/demoData'
import { Deal } from '@/types'

export default function DealsPage() {
  const [filter, setFilter] = useState('all')
  const [sortBy, setSortBy] = useState('score')
  const platforms = ['all', 'amazon', 'flipkart', 'myntra', 'croma']

  const filtered = (DEALS as unknown as Deal[])
    .filter(d => filter === 'all' || d.platform === filter)
    .sort((a, b) => {
      if (sortBy === 'score') return b.dealScore - a.dealScore
      if (sortBy === 'discount') return b.discount - a.discount
      return a.product.bestPrice - b.product.bestPrice
    })

  return (
    <div className="min-h-screen pt-32 pb-40">
      <div className="w-full max-w-[1536px] mx-auto px-8 md:px-16">
        <div className="mb-32 max-w-4xl">
          <span className="text-[0.75rem] font-medium uppercase tracking-[0.15em] block mb-8">Market Watch</span>
          <h1 className="text-[3rem] sm:text-[4.5rem] lg:text-[5.5rem] font-[var(--font-display)] font-medium leading-[1.05] tracking-tight text-theme-text mb-12">Verified Discounts.</h1>
          <p className="text-[1.125rem] sm:text-[1.25rem] leading-[1.6] tracking-tight text-theme-secondary">
            Algorithmic deal detection cutting through fake markups. Authentic drops only.
          </p>
        </div>

        <div className="flex flex-col md:flex-row md:items-end justify-between gap-12 mb-24 border-b border-theme-border pb-12">
          <div className="flex flex-wrap gap-8">
            {platforms.map(p => (
              <button key={p} onClick={() => setFilter(p)}
                className={`text-[0.75rem] font-medium uppercase tracking-[0.15em] transition-colors ${
                  filter === p ? 'text-theme-text' : 'text-theme-muted hover:text-theme-text'
                }`}
              >{p === 'all' ? 'ALL PLATFORMS' : (PLATFORMS as any)[p]?.name.toUpperCase()}</button>
            ))}
          </div>
          <select value={sortBy} onChange={e => setSortBy(e.target.value)}
            className="bg-transparent text-[0.875rem] font-medium text-theme-text focus:outline-none cursor-pointer pb-1 border-b border-transparent hover:border-theme-text transition-colors"
          >
            <option value="score" className="text-theme-bg">Sort: Algorithmic Score</option>
            <option value="discount" className="text-theme-bg">Sort: Maximum Discount</option>
            <option value="price" className="text-theme-bg">Sort: Lowest Price</option>
          </select>
        </div>

        {/* Minimal List Layout for Deals */}
        <div className="space-y-8">
           {/* Header Row */}
           <div className="hidden md:grid grid-cols-12 gap-12 text-[0.75rem] font-medium uppercase tracking-[0.15em] text-theme-muted border-b border-theme-border pb-6 px-12">
              <div className="col-span-6 lg:col-span-5">Product</div>
              <div className="col-span-2">Platform</div>
              <div className="col-span-2 text-right">Discount</div>
              <div className="col-span-2 text-right">Price</div>
           </div>

          {filtered.map((deal, i) => (
            <motion.div key={deal.id}
              initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
              transition={{ delay: Math.min(i * 0.05, 0.5), ease: [0.22, 1, 0.36, 1], duration: 0.8 }}
            >
              <Link href={`/product/${deal.product.id}`} className="group block bg-theme-elevated hover:bg-theme-subtle transition-colors p-10 lg:p-12 rounded-sm border border-transparent hover:border-theme-border">
                 <div className="grid grid-cols-1 md:grid-cols-12 gap-12 items-center">
                    
                    {/* Product */}
                    <div className="md:col-span-6 lg:col-span-5 flex items-center gap-8">
                       <div className="w-32 h-32 bg-theme-bg flex items-center justify-center p-6 shrink-0 mix-blend-screen overflow-hidden">
                          <img src={deal.product.image} alt={deal.product.name} className="max-w-full max-h-full object-contain group-hover:scale-110 transition-transform duration-700" />
                       </div>
                       <div>
                          <p className="text-[0.75rem] font-medium uppercase tracking-[0.15em] text-theme-muted mb-2">{deal.product.brand}</p>
                          <h3 className="text-[1.25rem] font-medium text-theme-text">{deal.product.name}</h3>
                          {deal.dealScore >= 85 && <span className="text-[0.65rem] uppercase tracking-widest text-[#22c55e] mt-4 block">Premium Deal Score {deal.dealScore}</span>}
                       </div>
                    </div>

                    {/* Platform */}
                    <div className="md:col-span-2 hidden md:block">
                       <span className="text-[0.875rem] text-theme-secondary">{(PLATFORMS as any)[deal.platform]?.name}</span>
                    </div>

                    {/* Discount */}
                    <div className="md:col-span-2 hidden md:flex justify-end">
                       <span className="inline-block border border-theme-text text-theme-text px-2 py-1 text-[0.75rem] font-medium">-{deal.discount}%</span>
                    </div>

                    {/* Price + Arrow */}
                    <div className="md:col-span-2 flex items-center justify-between md:justify-end gap-x-6">
                       <div className="text-left md:text-right">
                          <p className="text-[1.125rem] font-medium text-theme-text">{formatPrice(deal.product.bestPrice)}</p>
                          <p className="text-[0.875rem] text-theme-muted line-through">{formatPrice(deal.product.originalPrice)}</p>
                       </div>
                       <ArrowRight className="w-5 h-5 text-theme-dim group-hover:text-theme-text transition-colors shrink-0" strokeWidth={1.5} />
                    </div>

                 </div>
              </Link>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  )
}

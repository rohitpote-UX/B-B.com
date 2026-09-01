'use client'

import { motion } from 'framer-motion'
import { Star, ShieldCheck, Quote } from 'lucide-react'

const TESTIMONIALS = [
  {
    quote: "Brand Battle is the only engine that cuts through algorithmic affiliate noise. It extracts exact hardware value without the marketing fluff. An indispensable tool for our studio.",
    name: "Marcus Vance",
    role: "Lead Audio Engineer, Studio Berlin",
    image: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?q=80&w=200&auto=format&fit=crop",
    rating: 5,
  },
  {
    quote: "The historical price tracking mapped precisely to our internal procurement data. It stopped us from buying into fake deals that were marked up right before sales.",
    name: "Elena Rostova",
    role: "Head of Procurement, Nexus Tech",
    image: "https://images.unsplash.com/photo-1494790108377-be9c29b29330?q=80&w=200&auto=format&fit=crop",
    rating: 5,
  },
  {
    quote: "I've replaced my entire hardware review bookmark folder with this one dashboard. The spec-by-spec comparison interface is flawlessly engineered and strictly objective.",
    name: "David Chen",
    role: "Senior Hardware Specialist",
    image: "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?q=80&w=200&auto=format&fit=crop",
    rating: 5,
  },
]

export default function TestimonialsSection() {
  return (
    <section className="relative py-28 bg-[#07070b] text-white border-b border-white/10 overflow-hidden">
      {/* Background ambient lighting */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[400px] bg-[#ff1695]/5 blur-[160px] rounded-full pointer-events-none" />

      <div className="w-full max-w-[1536px] mx-auto px-6 sm:px-10 lg:px-16 relative z-10">
        
        {/* Header */}
        <div className="text-center max-w-3xl mx-auto mb-20">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/[0.04] border border-white/10 mb-4">
            <ShieldCheck className="w-3.5 h-3.5 text-[#ff1695]" />
            <span className="text-xs font-mono tracking-widest uppercase text-white/70">
              INDUSTRY CONSENSUS
            </span>
          </div>
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-[var(--font-display)] font-semibold tracking-tight uppercase">
            Trusted By <span className="text-[#ff1695] italic">Engineers & Professionals.</span>
          </h2>
        </div>

        {/* 3-Column Testimonial Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {TESTIMONIALS.map((item, idx) => (
            <motion.div
              key={idx}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6, delay: idx * 0.12 }}
              className="group relative rounded-3xl bg-white/[0.02] hover:bg-white/[0.04] border border-white/10 hover:border-[#ff1695]/40 p-8 backdrop-blur-2xl transition-all duration-500 shadow-xl flex flex-col justify-between"
            >
              <div>
                {/* Quote Icon & Stars */}
                <div className="flex justify-between items-center mb-6">
                  <div className="flex gap-1 text-amber-400">
                    {Array.from({ length: item.rating }).map((_, s) => (
                      <Star key={s} className="w-4 h-4 fill-amber-400" />
                    ))}
                  </div>
                  <Quote className="w-6 h-6 text-white/20 group-hover:text-[#ff1695]/50 transition-colors" />
                </div>

                <p className="text-sm sm:text-base text-white/80 font-light leading-relaxed mb-8">
                  &quot;{item.quote}&quot;
                </p>
              </div>

              {/* Author Info */}
              <div className="flex items-center gap-4 pt-6 border-t border-white/10">
                <div className="w-12 h-12 rounded-full overflow-hidden border border-white/20 shrink-0">
                  <img
                    src={item.image}
                    alt={item.name}
                    className="w-full h-full object-cover filter grayscale group-hover:grayscale-0 transition-all duration-700"
                  />
                </div>
                <div>
                  <h4 className="text-sm font-bold text-white group-hover:text-[#ff1695] transition-colors">
                    {item.name}
                  </h4>
                  <p className="text-xs font-mono text-white/50">{item.role}</p>
                </div>
              </div>

              {/* Border glow effect */}
              <div className="absolute inset-0 rounded-3xl bg-gradient-to-r from-[#ff1695]/0 via-[#ff1695]/10 to-[#ff1695]/0 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none" />
            </motion.div>
          ))}
        </div>

      </div>
    </section>
  )
}

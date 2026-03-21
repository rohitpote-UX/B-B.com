import { motion, useInView } from 'framer-motion'
import { useRef } from 'react'
import { Link } from 'react-router-dom'
import { ArrowRight, Star } from 'lucide-react'
import { PRODUCTS, DEALS } from '../data/demoData'

const TESTIMONIALS = [
  {
    quote: "Brand Battle is the only engine that cuts through the algorithmic noise. It extracts exact hardware value without the marketing fluff. A truly indispensable tool for our studio.",
    name: "Marcus V.",
    role: "Lead Audio Engineer, Studio Berlin",
    image: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?q=80&w=200&auto=format&fit=crop"
  },
  {
    quote: "The historical price tracking mapped precisely to our internal procurement data. It stopped us from buying into fake deals that were marked up the day before.",
    name: "Elena Rostova",
    role: "Head of Procurement, Nexus Tech",
    image: "https://images.unsplash.com/photo-1494790108377-be9c29b29330?q=80&w=200&auto=format&fit=crop"
  },
  {
    quote: "I've replaced my entire tech-review bookmark folder with this one dashboard. The spec-by-spec comparison interface is flawlessly engineered and strictly objective.",
    name: "David Chen",
    role: "Senior Hardware Reviewer",
    image: "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?q=80&w=200&auto=format&fit=crop"
  }
]

/* --- Animation Wrapper --- */
function FadeUp({ children, delay = 0, className = "" }) {
  const ref = useRef(null)
  const inView = useInView(ref, { once: true, margin: '-10%' })
  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 50 }}
      animate={inView ? { opacity: 1, y: 0 } : {}}
      transition={{ duration: 1, delay, ease: [0.22, 1, 0.36, 1] }}
      className={className}
    >
      {children}
    </motion.div>
  )
}

export default function LandingPage() {
  return (
    <div className="pb-32">
      {/* ─── 1. HERO SECTION ─── */}
      <section className="relative h-[120vh] flex items-center pt-20">
        <div className="w-full max-w-[1536px] mx-auto px-8 md:px-16 grid grid-cols-12 gap-8 lg:gap-16">
          <div className="col-span-12 lg:col-span-8 flex flex-col justify-center">
            <motion.div
              initial={{ opacity: 0, y: 50 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 1.2, ease: [0.22, 1, 0.36, 1] }}
            >
              <h1 className="text-[4rem] sm:text-[6rem] lg:text-[6.5rem] font-[var(--font-display)] font-medium leading-[13.5vh] uppercase tracking-tighter text-theme-text">
                The absolute<br />
                standard in<br />
                <span className='text-red-700 font-bold italic'>product</span> comparison.
              </h1>
              <p className="text-[1.125rem] sm:text-[1.25rem] leading-[1.6] tracking-tight max-w-lg mt-4">
                Minimal noise. Maximum clarity. Discover genuine deals and compare premium products across all major platforms with AI-driven precision.
              </p>
              <div className="flex flex-col sm:flex-row gap-8 mt-12">
                <Link to="/compare" className="inline-flex items-center justify-center px-10 py-5 bg-transparent border border-theme-text text-theme-text text-[0.875rem] font-medium tracking-wide transition-all duration-300 rounded-[2px] hover:bg-theme-text hover:text-theme-bg">
                  Start Comparison
                </Link>
                <Link to="/search" className="inline-flex items-center justify-center px-10 py-5 bg-transparent border border-theme-border text-theme-text text-[0.875rem] font-medium tracking-wide transition-all duration-300 rounded-[2px] hover:border-theme-text">
                  Explore Catalog
                </Link>
              </div>
            </motion.div>
          </div>

          <div className="col-span-12 lg:col-span-4 hidden lg:flex items-center justify-center">
            {/* Minimal hero art piece - Abstract representation of a product */}
            <motion.div 
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 1.5, delay: 0.2, ease: [0.22, 1, 0.36, 1] }}
              className="relative w-full aspect-[3/4] bg-theme-elevated flex items-center justify-center p-8"
            >
               <img src={PRODUCTS[0].image} alt="Featured Product" className="w-full h-full object-contain filter drop-shadow-2xl" />
               <div className="absolute bottom-10 left-10 text-[0.75rem] font-medium uppercase tracking-[0.15em]">Featured</div>
               <div className="absolute bottom-10 right-10 text-[0.75rem] font-medium uppercase tracking-[0.15em] text-theme-text">{PRODUCTS[0].name}</div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* ─── 2. PRODUCT SHOWCASE (GRID) ─── */}
      <section className="py-[140px] lg:py-[240px] border-t border-theme-border">
        <div className="w-full max-w-[1536px] mx-auto px-8 md:px-16">
          <FadeUp className="mb-32 flex flex-col md:flex-row md:items-end justify-between gap-12">
            <div>
              <span className="text-[0.75rem] font-medium uppercase tracking-[0.15em] block mb-8">Catalog</span>
              <h2 className="text-[2rem] sm:text-[3rem] lg:text-[3.5rem] font-medium leading-[1.1] tracking-tight text-theme-text">Curated Selection.</h2>
            </div>
             <Link to="/search" className="text-[0.75rem] font-medium uppercase tracking-[0.15em] hover:text-theme-text transition-colors flex items-center gap-2">
                View All <ArrowRight className="w-4 h-4" />
             </Link>
          </FadeUp>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-x-12 gap-y-24">
            {PRODUCTS.slice(0, 4).map((product, i) => (
              <FadeUp key={product.id} delay={i * 0.1}>
                <Link to={`/product/${product.id}`} className="group block">
                  <div className="aspect-square bg-theme-elevated p-8 lg:p-12 mb-10 flex items-center justify-center overflow-hidden">
                    <img src={product.image} alt={product.name} />
                  </div>
                  <div>
                    <h3 className="text-[1.25rem] font-medium text-theme-text tracking-tight mb-3">{product.name}</h3>
                    <p className="text-[1rem] text-theme-secondary mb-6">{product.brand}</p>
                    <div className="flex items-center justify-between">
                      <span className="text-[1.25rem] font-medium text-theme-text">${product.bestPrice}</span>
                    </div>
                  </div>
                </Link>
              </FadeUp>
            ))}
          </div>
        </div>
      </section>

      {/* ─── 3. FEATURE HIGHLIGHT (SPLIT) ─── */}
      <section className="py-[140px] lg:py-[240px] bg-theme-elevated">
        <div className="w-full max-w-[1536px] mx-auto px-8 md:px-16">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 lg:gap-[160px] items-center">
             <FadeUp className="order-2 lg:order-1 aspect-square bg-theme-bg flex items-center justify-center p-12 relative overflow-hidden">
                {/* Abstract graphical representation of analytics/tracking */}
                <div className="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/cubes.png')] opacity-5 mix-blend-overlay z-10 pointer-events-none"></div>
                <img 
                   src="https://images.unsplash.com/photo-1551288049-bebda4e38f71?q=80&w=800&auto=format&fit=crop" 
                   alt="90-Day Historical Price Tracking Data" 
                   className="w-full h-full object-cover filter grayscale contrast-125 opacity-60 mix-blend-screen hover:scale-105 transition-transform duration-[2s]"
                />
             </FadeUp>
             <FadeUp className="order-1 lg:order-2 lg:pl-20">
                <span className="text-[0.75rem] font-medium uppercase tracking-[0.15em] block mb-8">Intelligence</span>
                <h2 className="text-[3rem] sm:text-[4.5rem] lg:text-[5.5rem] font-[var(--font-display)] font-medium leading-[1.05] tracking-tight text-theme-text mb-12 "><span className='text-red-700 font-bold italic'>Data-driven</span> decisions.</h2>
                <p className="text-[1.125rem] sm:text-[1.25rem] leading-[1.6] tracking-tight mb-16 text-theme-muted">
                  We strip away the marketing noise. Our engine analyzes historical price trends, authenticates reviews, and scores deals in real-time, delivering the raw truth about what you are buying.
                </p>
                <ul className="space-y-8 mb-16">
                   {[
                     '90-Day Historical Price Tracking',
                     'Algorithmic Deal Authentication',
                     'Cross-Platform Price Aggregation'
                   ].map((item, i) => (
                      <li key={i} className="flex items-start gap-4 text-[1rem] text-theme-secondary border-b border-theme-border pb-6">
                         <span className="block mt-1 w-1.5 h-1.5 bg-theme-strong shrink-0" />
                         {item}
                      </li>
                   ))}
                </ul>
                <Link to="/about" className="inline-flex items-center justify-center px-10 py-5 bg-transparent border border-theme-border text-theme-text text-[0.875rem] font-medium tracking-wide transition-all duration-300 rounded-[2px] hover:border-theme-text">Read The Manifesto</Link>
             </FadeUp>
          </div>
        </div>
      </section>

      {/* ─── 4. VERIFIED DEALS ─── */}
      <section className="py-[140px] lg:py-[240px]">
        <div className="w-full max-w-[1536px] mx-auto px-8 md:px-16">
           <FadeUp className="mb-32 text-center">
              <span className="text-[0.75rem] font-medium uppercase tracking-[0.15em] block mb-8">Market Watch</span>
              <h2 className="text-[2rem] sm:text-[3rem] lg:text-[3.5rem] font-medium leading-[1.1] tracking-tight text-theme-text">Authenticated Deals.</h2>
           </FadeUp>

           <div className="grid grid-cols-1 md:grid-cols-3 gap-16">
              {DEALS.slice(0, 3).map((deal, i) => (
                 <FadeUp key={deal.id} delay={i * 0.1}>
                    <Link to={`/product/${deal.product.id}`} className="group block">
                       <div className="aspect-[4/3] bg-theme-elevated p-16 mb-10 flex items-center justify-center">
                          <img src={deal.product.image} alt={deal.product.name} className="max-h-full object-contain mix-blend-normal transition-transform duration-700 group-hover:scale-105" />
                       </div>
                       <div className="flex justify-between items-start">
                          <div>
                             <h4 className="text-[1.25rem] font-medium text-theme-text mb-3">{deal.product.name}</h4>
                             <p className="text-[0.75rem] font-medium uppercase tracking-[0.15em] text-theme-secondary">{deal.product.brand}</p>
                          </div>
                          <div className="text-right">
                             <p className="text-[1.25rem] font-medium text-theme-text">${deal.product.bestPrice}</p>
                             <p className="text-[1rem] text-theme-muted line-through">${deal.product.originalPrice}</p>
                          </div>
                       </div>
                    </Link>
                 </FadeUp>
              ))}
           </div>
           
           <FadeUp className="mt-16 text-center">
              <Link to="/deals" className="inline-flex items-center justify-center px-10 py-5 bg-transparent border border-theme-border text-theme-text text-[0.875rem] font-medium tracking-wide transition-all duration-300 rounded-[2px] hover:border-theme-text">View All Deals</Link>
           </FadeUp>
        </div>
      </section>

      {/* ─── 5. TESTIMONIALS ─── */}
      <section className="py-[140px] lg:py-[240px] border-t border-theme-border">
        <div className="w-full max-w-[1536px] mx-auto px-8 md:px-16">
           <FadeUp className="mb-24 text-center">
              <span className="text-[0.75rem] font-medium uppercase tracking-[0.15em] block mb-8 text-theme-muted">Industry Consensus</span>
              <h2 className="text-[2rem] sm:text-[3rem] lg:text-[4.5rem] font-[var(--font-display)] font-medium leading-[1.1] tracking-tight text-theme-text mb-8">Trusted by professionals.</h2>
           </FadeUp>
           
           <div className="grid grid-cols-1 md:grid-cols-3 gap-8 lg:gap-12">
             {TESTIMONIALS.map((t, i) => (
                <FadeUp key={i} delay={i * 0.15}>
                   <motion.div 
                      whileHover={{ y: -8 }}
                      transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
                      className="h-full bg-theme-elevated p-10 lg:p-14 border border-transparent hover:border-theme-strong transition-colors duration-500 flex flex-col justify-between group"
                   >
                      <div>
                         <div className="flex gap-1 mb-8 opacity-70 group-hover:opacity-100 transition-opacity duration-500">
                            {[1, 2, 3, 4, 5].map(s => <Star key={s} className="w-4 h-4 text-theme-text fill-theme-text" />)}
                         </div>
                         <p className="text-[1.125rem] leading-[1.6] tracking-tight text-theme-secondary group-hover:text-theme-text transition-colors duration-500 mb-12">
                           "{t.quote}"
                         </p>
                      </div>
                      
                      <div className="flex items-center gap-6 border-t border-theme-border pt-8">
                         <div className="w-14 h-14 rounded-full overflow-hidden bg-theme-subtle shrink-0 pointer-events-none">
                            <motion.img 
                               src={t.image} 
                               alt={t.name}
                               className="w-full h-full object-cover filter grayscale opacity-80 group-hover:grayscale-0 group-hover:opacity-100 transition-all duration-[1s] ease-out" 
                               whileHover={{ scale: 1.15 }} // Since it's inside the motion div, it inherits group behaviors, but we'll manage scale via CSS or motion hover manually. It's safer to use group-hover class.
                            />
                         </div>
                         <div>
                            <h4 className="text-[1.125rem] font-medium text-theme-text tracking-tight">{t.name}</h4>
                            <p className="text-[0.75rem] uppercase tracking-[0.1em] text-theme-muted mt-2">{t.role}</p>
                         </div>
                      </div>
                   </motion.div>
                </FadeUp>
             ))}
           </div>
        </div>
      </section>

    </div>
  )
}

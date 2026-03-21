import { useState } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { ArrowLeft, Mail, Lock } from 'lucide-react'

export default function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')

  const handleLogin = (e) => {
     e.preventDefault()
     if (email && password) {
        localStorage.setItem('bb_user', JSON.stringify({ email }))
        window.location.href = '/profile'
     }
  }

  return (
    <div className="min-h-screen flex bg-theme-bg relative z-50">
      {/* Return to home button */}
      <Link to="/" className="absolute top-8 left-8 lg:left-12 flex items-center gap-2 text-[0.75rem] font-medium uppercase tracking-[0.15em] text-theme-secondary hover:text-theme-text transition-colors z-50">
         <ArrowLeft className="w-4 h-4" /> Home
      </Link>

      {/* Left panel - Branding */}
      <div className="hidden lg:flex w-[40%] bg-theme-elevated p-16 flex-col justify-between border-r border-theme-border pt-40">
         <div className="mb-24">
            <motion.h2 
               initial={{ opacity: 0, y: 30 }} 
               animate={{ opacity: 1, y: 0 }} 
               transition={{ duration: 0.8, ease: [0.22, 1, 0.36, 1] }}
               className="text-[4.5rem] font-[var(--font-display)] tracking-tight leading-[1] text-theme-text mb-8"
            >
               Welcome<br />Back.
            </motion.h2>
            <motion.p 
               initial={{ opacity: 0 }} 
               animate={{ opacity: 1 }} 
               transition={{ duration: 1, delay: 0.3 }}
               className="text-[1.125rem] text-theme-secondary leading-relaxed max-w-sm"
            >
               Access your objective hardware analytics dashboard and saved market sweeps.
            </motion.p>
         </div>
         <div className="text-[0.75rem] font-medium uppercase tracking-[0.15em] text-theme-muted">
             Secure Infrastructure Active
         </div>
      </div>

      {/* Right panel - Form */}
      <div className="flex-1 flex flex-col justify-center px-8 lg:px-24 xl:px-32">
         <div className="w-full max-w-md mx-auto">
            <Link to="/" className="lg:hidden text-xl font-medium tracking-tight font-[var(--font-display)] block mb-12 mt-32">
              BRAND<span className="text-theme-secondary">BATTLE</span>
            </Link>
            
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1], delay: 0.1 }}>
               <h1 className="text-[2.5rem] font-[var(--font-display)] font-medium text-theme-text mb-2 lg:hidden tracking-tight">Welcome Back.</h1>
               <span className="text-[0.75rem] font-medium uppercase tracking-[0.15em] block mb-16 text-theme-secondary">Identify Credentials</span>

               <form onSubmit={handleLogin} className="space-y-12">
                  <div className="relative group">
                     <Mail className="absolute left-0 top-3 w-5 h-5 text-theme-muted group-focus-within:text-theme-text transition-colors" />
                     <input 
                        type="email" 
                        value={email}
                        onChange={e => setEmail(e.target.value)}
                        placeholder="EMAIL ADDRESS"
                        className="w-full bg-transparent border-b border-theme-border py-3 pl-10 pr-4 text-[0.875rem] font-medium uppercase tracking-[0.1em] text-theme-text placeholder:text-theme-muted focus:outline-none focus:border-theme-text transition-colors"
                     />
                  </div>
                  
                  <div className="relative group">
                     <Lock className="absolute left-0 top-3 w-5 h-5 text-theme-muted group-focus-within:text-theme-text transition-colors" />
                     <input 
                        type="password" 
                        value={password}
                        onChange={e => setPassword(e.target.value)}
                        placeholder="SECURE PASSWORD"
                        className="w-full bg-transparent border-b border-theme-border py-3 pl-10 pr-4 text-[0.875rem] font-medium uppercase tracking-[0.1em] text-theme-text placeholder:text-theme-muted focus:outline-none focus:border-theme-text transition-colors"
                     />
                     <div className="absolute right-0 top-3">
                         <Link to="#" className="text-[0.65rem] uppercase tracking-widest text-theme-secondary hover:text-theme-text transition-colors">Forgot?</Link>
                     </div>
                  </div>

                  <button className="w-full inline-flex items-center justify-center px-10 py-5 bg-theme-text border border-theme-text text-theme-bg text-[0.875rem] font-medium tracking-[0.15em] uppercase transition-transform duration-300 hover:scale-[1.02] rounded-[2px] mt-12 cursor-pointer shadow-lg shadow-black/10">
                     Authenticate
                  </button>
               </form>

               <p className="mt-16 text-center text-[0.875rem] text-theme-secondary">
                  No access clearance? <Link to="/signup" className="text-theme-text font-medium border-b border-transparent hover:border-theme-text transition-all duration-300 ml-2 py-0.5">Request Account</Link>
               </p>
            </motion.div>
         </div>
      </div>
    </div>
  )
}

'use client'

import { useState } from 'react'
import Link from 'next/link'
import { motion, AnimatePresence } from 'framer-motion'
import {
  ArrowLeft,
  Mail,
  Lock,
  Eye,
  EyeOff,
  ShieldCheck,
  CheckCircle2,
  LockKeyhole,
  Sparkles,
  ArrowRight,
  Loader2,
  AlertCircle
} from 'lucide-react'

export default function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [rememberMe, setRememberMe] = useState(true)
  const [authStep, setAuthStep] = useState<'idle' | 'verifying' | 'authenticated' | 'ready'>('idle')
  const [errorMessage, setErrorMessage] = useState('')

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault()
    setErrorMessage('')

    if (!email || !password) {
      setErrorMessage("We couldn't verify your credentials. Please enter both email and password.")
      return
    }

    // Step-by-step morphing authentication experience
    setAuthStep('verifying')

    setTimeout(() => {
      setAuthStep('authenticated')
      localStorage.setItem('bb_user', JSON.stringify({ email }))
      document.cookie = "bb_user=true; path=/; max-age=86400; SameSite=Lax"

      setTimeout(() => {
        setAuthStep('ready')
        setTimeout(() => {
          window.location.href = '/profile'
        }, 800)
      }, 1000)
    }, 1200)
  }

  return (
    <div className="min-h-screen flex bg-[#050505] text-white relative z-50 overflow-hidden font-sans">
      {/* Return to home button */}
      <Link
        href="/"
        className="absolute top-8 left-8 lg:left-12 flex items-center gap-2 text-xs font-mono uppercase tracking-[0.2em] text-white/50 hover:text-white transition-colors z-50 min-h-[44px]"
      >
        <ArrowLeft className="w-4 h-4" /> Home
      </Link>

      {/* ─── LEFT PANEL: EDITORIAL BRANDING & TRUST TIMELINE ─── */}
      <div className="hidden lg:flex w-[46%] bg-[#08080c] p-16 flex-col justify-between border-r border-white/10 pt-36 relative overflow-hidden">
        {/* Subtle background glow */}
        <div className="absolute top-1/3 left-10 w-96 h-96 bg-[#ff1695]/10 blur-[140px] rounded-full pointer-events-none" />

        <div className="relative z-10 space-y-8">
          {/* Staggered Line-by-Line Headline */}
          <div className="space-y-1">
            <motion.span
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.1 }}
              className="text-xs font-mono text-[#ff1695] uppercase tracking-widest font-bold block mb-3"
            >
              AUTHENTICATION V2.0 ✦ ENTERPRISE CLEARANCE
            </motion.span>

            <motion.h2
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.7, delay: 0.2 }}
              className="text-[3.25rem] xl:text-[4rem] font-[var(--font-display)] font-semibold tracking-tight leading-[0.98] uppercase text-white"
            >
              WELCOME BACK TO<br />
              <span className="text-[#ff1695] italic">THE MOST TRUSTED</span><br />
              PRODUCT<br />
              INTELLIGENCE<br />
              PLATFORM.
            </motion.h2>
          </div>

          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.8, delay: 0.4 }}
            className="text-white/60 text-sm xl:text-base font-light leading-relaxed max-w-md"
          >
            Millions of product decisions are made using advertisements. BrandBattle helps you make yours using verified information.
          </motion.p>

          {/* Animated Vertical Trust Timeline */}
          <div className="pt-6 border-t border-white/10 space-y-3 font-mono text-xs text-white/70">
            <span className="text-[0.65rem] text-white/40 uppercase tracking-widest font-bold block mb-2">
              REAL-TIME SECURITY TIMELINE
            </span>
            <div className="flex items-center gap-3">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              <span>Authentication ➔ Verification ➔ Recommendation ➔ Decision</span>
            </div>
            <div className="flex items-center gap-4 text-[0.65rem] text-white/40 pt-1">
              <span>✔ 99% Data Accuracy Goal</span>
              <span>•</span>
              <span>✔ 256-Bit SSL Encryption</span>
            </div>
          </div>
        </div>

        <div className="relative z-10 flex items-center justify-between text-xs font-mono text-white/40 pt-6 border-t border-white/10">
          <span>SECURE INFRASTRUCTURE ACTIVE</span>
          <span className="text-emerald-400">● 100% OPERATIONAL</span>
        </div>
      </div>

      {/* ─── RIGHT PANEL: FLOATING DARK GLASS CARD & FORM ─── */}
      <div className="flex-1 flex flex-col justify-center px-6 sm:px-12 lg:px-20 xl:px-28 relative">
        <div className="w-full max-w-md mx-auto">
          {/* Mobile Header */}
          <Link href="/" className="lg:hidden text-2xl font-bold tracking-tight font-[var(--font-display)] block mb-8 mt-24">
            BRAND<span className="text-[#ff1695]">BATTLE</span>
          </Link>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="rounded-3xl bg-gradient-to-b from-white/[0.04] to-white/[0.01] border border-white/15 p-6 sm:p-10 backdrop-blur-2xl shadow-2xl relative overflow-hidden"
          >
            <div className="mb-8">
              <span className="text-[0.65rem] font-mono uppercase tracking-[0.2em] text-[#ff1695] font-bold block mb-1">
                IDENTIFY CREDENTIALS
              </span>
              <h1 className="text-2xl sm:text-3xl font-bold font-[var(--font-display)] text-white tracking-tight uppercase">
                Secure Sign In
              </h1>
            </div>

            {/* Error Card */}
            <AnimatePresence>
              {errorMessage && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  className="mb-6 p-3.5 rounded-2xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs font-mono flex items-start gap-2.5"
                >
                  <AlertCircle className="w-4 h-4 shrink-0 mt-0.5 text-rose-400" />
                  <span>{errorMessage}</span>
                </motion.div>
              )}
            </AnimatePresence>

            <form onSubmit={handleLogin} className="space-y-6">
              {/* Email Input */}
              <div className="space-y-1.5">
                <label className="text-[0.65rem] font-mono uppercase tracking-widest text-white/60 block font-semibold">
                  Email Address
                </label>
                <div className="relative group">
                  <Mail className="absolute left-3.5 top-3.5 w-4 h-4 text-white/40 group-focus-within:text-[#ff1695] transition-colors" />
                  <input
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="name@company.com"
                    className="w-full bg-white/[0.03] border border-white/10 rounded-xl py-3 pl-10 pr-4 text-xs font-mono text-white placeholder:text-white/30 focus:outline-none focus:border-[#ff1695] focus:ring-1 focus:ring-[#ff1695]/40 transition-all min-h-[44px]"
                  />
                </div>
              </div>

              {/* Password Input */}
              <div className="space-y-1.5">
                <div className="flex justify-between items-center">
                  <label className="text-[0.65rem] font-mono uppercase tracking-widest text-white/60 font-semibold">
                    Secure Password
                  </label>
                  <Link href="#" className="text-[0.65rem] font-mono uppercase tracking-wider text-[#ff1695] hover:underline">
                    Forgot Password?
                  </Link>
                </div>
                <div className="relative group">
                  <Lock className="absolute left-3.5 top-3.5 w-4 h-4 text-white/40 group-focus-within:text-[#ff1695] transition-colors" />
                  <input
                    type={showPassword ? 'text' : 'password'}
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••••••"
                    className="w-full bg-white/[0.03] border border-white/10 rounded-xl py-3 pl-10 pr-10 text-xs font-mono text-white placeholder:text-white/30 focus:outline-none focus:border-[#ff1695] focus:ring-1 focus:ring-[#ff1695]/40 transition-all min-h-[44px]"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3.5 top-3.5 text-white/40 hover:text-white transition-colors"
                  >
                    {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>

              {/* Remember Me Checkbox */}
              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="remember"
                  checked={rememberMe}
                  onChange={(e) => setRememberMe(e.target.checked)}
                  className="rounded border-white/20 bg-white/5 text-[#ff1695] focus:ring-0 cursor-pointer"
                />
                <label htmlFor="remember" className="text-xs font-mono text-white/60 cursor-pointer select-none">
                  Remember authentication session for 30 days
                </label>
              </div>

              {/* Primary Submit Button with State Morph */}
              <button
                type="submit"
                disabled={authStep !== 'idle'}
                className="w-full py-4 bg-[#ff1695] text-white text-xs font-mono font-bold uppercase tracking-[0.2em] rounded-xl hover:bg-[#e00d7f] transition-all duration-300 shadow-[0_0_25px_rgba(255,22,149,0.4)] flex items-center justify-center gap-2 cursor-pointer min-h-[48px]"
              >
                {authStep === 'idle' && (
                  <>
                    <span>Continue Securely</span>
                    <ArrowRight className="w-4 h-4" />
                  </>
                )}
                {authStep === 'verifying' && (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>Verifying Credentials...</span>
                  </>
                )}
                {authStep === 'authenticated' && (
                  <>
                    <CheckCircle2 className="w-4 h-4 text-emerald-300" />
                    <span>Authenticated ✦ Loading Dashboard...</span>
                  </>
                )}
                {authStep === 'ready' && (
                  <>
                    <Sparkles className="w-4 h-4" />
                    <span>Dashboard Ready ➔ Redirecting</span>
                  </>
                )}
              </button>
            </form>

            {/* Optional SSO Architecture Section */}
            <div className="mt-6 pt-6 border-t border-white/10 space-y-3">
              <span className="text-[0.6rem] font-mono text-white/40 uppercase tracking-widest block text-center">
                ENTERPRISE SINGLE SIGN-ON PROVIDERS
              </span>
              <div className="grid grid-cols-2 gap-2">
                <button
                  type="button"
                  onClick={() => alert("SSO Integration: OAuth 2.0 provider active.")}
                  className="py-2.5 px-3 rounded-xl bg-white/[0.03] border border-white/10 hover:border-white/20 text-[0.65rem] font-mono text-white/80 transition-all flex items-center justify-center gap-2"
                >
                  <span>Google</span>
                </button>
                <button
                  type="button"
                  onClick={() => alert("SSO Integration: OAuth 2.0 provider active.")}
                  className="py-2.5 px-3 rounded-xl bg-white/[0.03] border border-white/10 hover:border-white/20 text-[0.65rem] font-mono text-white/80 transition-all flex items-center justify-center gap-2"
                >
                  <span>Apple</span>
                </button>
              </div>
            </div>

            <p className="mt-6 text-center text-xs font-mono text-white/50">
              No access clearance?{' '}
              <Link href="/signup" className="text-[#ff1695] font-bold hover:underline">
                Request Account
              </Link>
            </p>
          </motion.div>
        </div>
      </div>
    </div>
  )
}

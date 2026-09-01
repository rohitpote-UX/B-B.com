'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { motion, AnimatePresence } from 'framer-motion'
import {
  ArrowLeft,
  User,
  Mail,
  Lock,
  Eye,
  EyeOff,
  CheckCircle2,
  AlertCircle,
  Loader2,
  Sparkles,
  Check,
  Shield
} from 'lucide-react'
import PasswordStrengthMeter from '@/components/auth/PasswordStrengthMeter'

export default function SignupPage() {
  const [name, setName] = useState('')
  const [username, setUsername] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [agreeTerms, setAgreeTerms] = useState(true)
  const [receiveAlerts, setReceiveAlerts] = useState(false)

  // Live Validation States
  const [usernameStatus, setUsernameStatus] = useState<'idle' | 'checking' | 'available' | 'taken'>('idle')
  const [emailStatus, setEmailStatus] = useState<'idle' | 'valid' | 'disposable' | 'invalid'>('idle')
  const [isSuccessMorph, setIsSuccessMorph] = useState(false)
  const [errorMessage, setErrorMessage] = useState('')

  // Live Username Check Simulation
  useEffect(() => {
    if (!username || username.length < 3) {
      setUsernameStatus('idle')
      return
    }
    setUsernameStatus('checking')
    const timer = setTimeout(() => {
      if (username.toLowerCase().includes('admin') || username.toLowerCase() === 'taken') {
        setUsernameStatus('taken')
      } else {
        setUsernameStatus('available')
      }
    }, 400)
    return () => clearTimeout(timer)
  }, [username])

  // Live Email Validation Simulation
  useEffect(() => {
    if (!email) {
      setEmailStatus('idle')
      return
    }
    if (!email.includes('@') || !email.includes('.')) {
      setEmailStatus('invalid')
      return
    }
    if (email.includes('tempmail') || email.includes('mailinator')) {
      setEmailStatus('disposable')
    } else {
      setEmailStatus('valid')
    }
  }, [email])

  const handleSignup = (e: React.FormEvent) => {
    e.preventDefault()
    setErrorMessage('')

    if (!name || !username || !email || !password) {
      setErrorMessage('Please fill in all required fields.')
      return
    }

    if (password !== confirmPassword) {
      setErrorMessage('Passwords do not match. Please re-enter your password.')
      return
    }

    if (!agreeTerms) {
      setErrorMessage('You must agree to the Terms of Service and Privacy Policy.')
      return
    }

    // Trigger Success Morph Experience
    setIsSuccessMorph(true)
    localStorage.setItem('bb_user', JSON.stringify({ name, username, email }))
    document.cookie = "bb_user=true; path=/; max-age=86400; SameSite=Lax"

    setTimeout(() => {
      window.location.href = '/profile'
    }, 2800)
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

      {/* ─── LEFT PANEL: EDITORIAL BRANDING ─── */}
      <div className="hidden lg:flex w-[46%] bg-[#08080c] p-16 flex-col justify-between border-r border-white/10 pt-36 relative overflow-hidden">
        <div className="absolute top-1/3 left-10 w-96 h-96 bg-[#ff1695]/10 blur-[140px] rounded-full pointer-events-none" />

        <div className="relative z-10 space-y-8">
          <motion.span
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="text-xs font-mono text-[#ff1695] uppercase tracking-widest font-bold block mb-3"
          >
            ACCOUNT REGISTRATION ✦ TRUST PLATFORM
          </motion.span>

          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.2 }}
            className="text-[3.25rem] xl:text-[4rem] font-[var(--font-display)] font-semibold tracking-tight leading-[0.98] uppercase text-white"
          >
            YOUR PRODUCT<br />
            JOURNEY<br />
            <span className="text-[#ff1695] italic">STARTS WITH</span><br />
            TRUST.
          </motion.h2>

          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.8, delay: 0.4 }}
            className="text-white/60 text-sm xl:text-base font-light leading-relaxed max-w-md"
          >
            Join the platform that cuts through marketing noise. Get objective hardware analytics, price consensus audits, and verified deals.
          </motion.p>
        </div>

        <div className="relative z-10 flex items-center justify-between text-xs font-mono text-white/40 pt-6 border-t border-white/10">
          <span>SECURE INFRASTRUCTURE ACTIVE</span>
          <span className="text-emerald-400">● 100% OPERATIONAL</span>
        </div>
      </div>

      {/* ─── RIGHT PANEL: FLOATING DARK GLASS CARD & FORM ─── */}
      <div className="flex-1 flex flex-col justify-center px-6 sm:px-12 lg:px-20 xl:px-28 relative my-12 lg:my-0">
        <div className="w-full max-w-md mx-auto">
          {/* Mobile Header */}
          <Link href="/" className="lg:hidden text-2xl font-bold tracking-tight font-[var(--font-display)] block mb-8 mt-20">
            BRAND<span className="text-[#ff1695]">BATTLE</span>
          </Link>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="rounded-3xl bg-gradient-to-b from-white/[0.04] to-white/[0.01] border border-white/15 p-6 sm:p-10 backdrop-blur-2xl shadow-2xl relative overflow-hidden"
          >
            {/* SUCCESS SCREEN MORPH */}
            <AnimatePresence>
              {isSuccessMorph ? (
                <motion.div
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.95 }}
                  className="py-12 text-center space-y-4"
                >
                  <div className="w-16 h-16 rounded-full bg-emerald-500/20 border border-emerald-500/50 flex items-center justify-center text-emerald-400 mx-auto shadow-[0_0_30px_rgba(52,211,153,0.3)]">
                    <CheckCircle2 className="w-8 h-8" />
                  </div>

                  <h3 className="text-xl sm:text-2xl font-bold font-[var(--font-display)] uppercase text-white">
                    Welcome, {name || 'User'}
                  </h3>

                  <p className="text-xs font-mono text-emerald-400 font-bold">
                    ACCOUNT CREATED SUCCESSFULLY ✦ 256-BIT ENCRYPTED
                  </p>

                  <p className="text-xs font-mono text-white/60 pt-2">
                    Preparing your personalized product intelligence dashboard...
                  </p>

                  <div className="flex justify-center items-center gap-2 pt-4 text-xs font-mono text-[#ff1695]">
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>Redirecting in 3s...</span>
                  </div>
                </motion.div>
              ) : (
                <>
                  <div className="mb-6">
                    <span className="text-[0.65rem] font-mono uppercase tracking-[0.2em] text-[#ff1695] font-bold block mb-1">
                      ESTABLISH IDENTITY
                    </span>
                    <h1 className="text-2xl sm:text-3xl font-bold font-[var(--font-display)] text-white tracking-tight uppercase">
                      Create Account
                    </h1>
                  </div>

                  {/* Error Card */}
                  {errorMessage && (
                    <div className="mb-4 p-3.5 rounded-2xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs font-mono flex items-start gap-2.5">
                      <AlertCircle className="w-4 h-4 shrink-0 mt-0.5 text-rose-400" />
                      <span>{errorMessage}</span>
                    </div>
                  )}

                  <form onSubmit={handleSignup} className="space-y-4">
                    {/* Full Name */}
                    <div className="space-y-1">
                      <label className="text-[0.65rem] font-mono uppercase tracking-widest text-white/60 block font-semibold">
                        Full Name
                      </label>
                      <div className="relative group">
                        <User className="absolute left-3.5 top-3.5 w-4 h-4 text-white/40 group-focus-within:text-[#ff1695] transition-colors" />
                        <input
                          type="text"
                          required
                          value={name}
                          onChange={(e) => setName(e.target.value)}
                          placeholder="Rohit Pote"
                          className="w-full bg-white/[0.03] border border-white/10 rounded-xl py-3 pl-10 pr-4 text-xs font-mono text-white placeholder:text-white/30 focus:outline-none focus:border-[#ff1695] focus:ring-1 focus:ring-[#ff1695]/40 transition-all min-h-[44px]"
                        />
                      </div>
                    </div>

                    {/* Username with Live Availability Indicator */}
                    <div className="space-y-1">
                      <div className="flex justify-between items-center">
                        <label className="text-[0.65rem] font-mono uppercase tracking-widest text-white/60 font-semibold">
                          Username
                        </label>
                        {usernameStatus === 'checking' && <span className="text-[0.65rem] font-mono text-amber-400">Checking...</span>}
                        {usernameStatus === 'available' && <span className="text-[0.65rem] font-mono text-emerald-400 font-bold">✔ Available</span>}
                        {usernameStatus === 'taken' && <span className="text-[0.65rem] font-mono text-rose-400 font-bold">✖ Taken</span>}
                      </div>
                      <div className="relative group">
                        <span className="absolute left-3.5 top-3.5 text-xs font-mono text-white/40">@</span>
                        <input
                          type="text"
                          required
                          value={username}
                          onChange={(e) => setUsername(e.target.value)}
                          placeholder="rohit_pote"
                          className="w-full bg-white/[0.03] border border-white/10 rounded-xl py-3 pl-10 pr-4 text-xs font-mono text-white placeholder:text-white/30 focus:outline-none focus:border-[#ff1695] focus:ring-1 focus:ring-[#ff1695]/40 transition-all min-h-[44px]"
                        />
                      </div>
                    </div>

                    {/* Email Input */}
                    <div className="space-y-1">
                      <div className="flex justify-between items-center">
                        <label className="text-[0.65rem] font-mono uppercase tracking-widest text-white/60 font-semibold">
                          Email Address
                        </label>
                        {emailStatus === 'disposable' && (
                          <span className="text-[0.65rem] font-mono text-amber-400 font-bold">⚠️ Disposable Domain</span>
                        )}
                      </div>
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
                    <div className="space-y-1">
                      <label className="text-[0.65rem] font-mono uppercase tracking-widest text-white/60 block font-semibold">
                        Create Password
                      </label>
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

                    {/* Password Strength Meter Component */}
                    <PasswordStrengthMeter password={password} />

                    {/* Confirm Password */}
                    <div className="space-y-1">
                      <label className="text-[0.65rem] font-mono uppercase tracking-widest text-white/60 block font-semibold">
                        Confirm Password
                      </label>
                      <input
                        type="password"
                        required
                        value={confirmPassword}
                        onChange={(e) => setConfirmPassword(e.target.value)}
                        placeholder="••••••••••••"
                        className="w-full bg-white/[0.03] border border-white/10 rounded-xl py-3 px-4 text-xs font-mono text-white placeholder:text-white/30 focus:outline-none focus:border-[#ff1695] focus:ring-1 focus:ring-[#ff1695]/40 transition-all min-h-[44px]"
                      />
                    </div>

                    {/* Agreement Checkboxes */}
                    <div className="space-y-2 pt-1">
                      <div className="flex items-start gap-2">
                        <input
                          type="checkbox"
                          id="terms"
                          checked={agreeTerms}
                          onChange={(e) => setAgreeTerms(e.target.checked)}
                          className="mt-0.5 rounded border-white/20 bg-white/5 text-[#ff1695] focus:ring-0 cursor-pointer"
                        />
                        <label htmlFor="terms" className="text-[0.7rem] font-mono text-white/60 leading-tight cursor-pointer select-none">
                          I agree to BrandBattle <Link href="#" className="text-[#ff1695] underline">Privacy Policy</Link> and <Link href="#" className="text-[#ff1695] underline">Terms of Service</Link>.
                        </label>
                      </div>

                      <div className="flex items-start gap-2">
                        <input
                          type="checkbox"
                          id="alerts"
                          checked={receiveAlerts}
                          onChange={(e) => setReceiveAlerts(e.target.checked)}
                          className="mt-0.5 rounded border-white/20 bg-white/5 text-[#ff1695] focus:ring-0 cursor-pointer"
                        />
                        <label htmlFor="alerts" className="text-[0.7rem] font-mono text-white/60 leading-tight cursor-pointer select-none">
                          Receive verified price drop alerts & market summaries (Optional).
                        </label>
                      </div>
                    </div>

                    {/* Submit Button */}
                    <button
                      type="submit"
                      className="w-full py-4 bg-[#ff1695] text-white text-xs font-mono font-bold uppercase tracking-[0.2em] rounded-xl hover:bg-[#e00d7f] transition-all duration-300 shadow-[0_0_25px_rgba(255,22,149,0.4)] cursor-pointer min-h-[48px] mt-2"
                    >
                      Create Secure Account
                    </button>
                  </form>

                  <p className="mt-6 text-center text-xs font-mono text-white/50">
                    Already hold clearance?{' '}
                    <Link href="/login" className="text-[#ff1695] font-bold hover:underline">
                      Authenticate
                    </Link>
                  </p>
                </>
              )}
            </AnimatePresence>
          </motion.div>
        </div>
      </div>
    </div>
  )
}

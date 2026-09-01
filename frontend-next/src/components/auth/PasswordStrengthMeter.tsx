'use client'

import { useMemo } from 'react'
import { Shield, ShieldAlert, ShieldCheck, Check, X } from 'lucide-react'

interface PasswordStrengthProps {
  password: string
}

export default function PasswordStrengthMeter({ password }: PasswordStrengthProps) {
  const analysis = useMemo(() => {
    if (!password) {
      return {
        score: 0,
        tier: 'Weak',
        color: 'bg-white/20',
        textColor: 'text-white/40',
        crackTime: 'Instant',
        hasMinLength: false,
        hasUpper: false,
        hasNum: false,
        hasSym: false,
      }
    }

    const hasMinLength = password.length >= 8
    const hasUpper = /[A-Z]/.test(password)
    const hasNum = /[0-9]/.test(password)
    const hasSym = /[^a-zA-Z0-9]/.test(password)

    let score = 0
    if (hasMinLength) score += 25
    if (hasUpper) score += 25
    if (hasNum) score += 25
    if (hasSym) score += 25

    let tier = 'Weak'
    let color = 'bg-rose-500'
    let textColor = 'text-rose-400'
    let crackTime = 'Seconds'

    if (score >= 100) {
      tier = 'Ultra'
      color = 'bg-emerald-400 shadow-[0_0_12px_rgba(52,211,153,0.5)]'
      textColor = 'text-emerald-400'
      crackTime = '34 Years'
    } else if (score >= 75) {
      tier = 'Strong'
      color = 'bg-emerald-500'
      textColor = 'text-emerald-400'
      crackTime = '3 Months'
    } else if (score >= 50) {
      tier = 'Good'
      color = 'bg-amber-400'
      textColor = 'text-amber-400'
      crackTime = '3 Days'
    } else if (score >= 25) {
      tier = 'Fair'
      color = 'bg-amber-500'
      textColor = 'text-amber-400'
      crackTime = '12 Hours'
    }

    return {
      score,
      tier,
      color,
      textColor,
      crackTime,
      hasMinLength,
      hasUpper,
      hasNum,
      hasSym,
    }
  }, [password])

  if (!password) return null

  return (
    <div className="space-y-2.5 p-3 rounded-2xl bg-white/[0.02] border border-white/10 text-xs font-mono">
      <div className="flex items-center justify-between">
        <span className="text-[0.65rem] text-white/50 uppercase tracking-wider font-semibold">
          PASSWORD STRENGTH & ENTROPY SCORE
        </span>
        <span className={`font-bold ${analysis.textColor}`}>
          {analysis.tier} ({analysis.score}%) · Est. Crack Time: {analysis.crackTime}
        </span>
      </div>

      {/* Strength Bar */}
      <div className="h-1.5 w-full bg-white/10 rounded-full overflow-hidden flex gap-1">
        <div
          className={`h-full transition-all duration-500 rounded-full ${analysis.color}`}
          style={{ width: `${analysis.score}%` }}
        />
      </div>

      {/* Rules Checklist Grid */}
      <div className="grid grid-cols-2 gap-1.5 pt-1 text-[0.65rem]">
        <div className={`flex items-center gap-1.5 ${analysis.hasMinLength ? 'text-emerald-400 font-semibold' : 'text-white/40'}`}>
          {analysis.hasMinLength ? <Check className="w-3 h-3" /> : <X className="w-3 h-3" />}
          <span>Min 8 characters</span>
        </div>

        <div className={`flex items-center gap-1.5 ${analysis.hasUpper ? 'text-emerald-400 font-semibold' : 'text-white/40'}`}>
          {analysis.hasUpper ? <Check className="w-3 h-3" /> : <X className="w-3 h-3" />}
          <span>Uppercase letter</span>
        </div>

        <div className={`flex items-center gap-1.5 ${analysis.hasNum ? 'text-emerald-400 font-semibold' : 'text-white/40'}`}>
          {analysis.hasNum ? <Check className="w-3 h-3" /> : <X className="w-3 h-3" />}
          <span>Number (0-9)</span>
        </div>

        <div className={`flex items-center gap-1.5 ${analysis.hasSym ? 'text-emerald-400 font-semibold' : 'text-white/40'}`}>
          {analysis.hasSym ? <Check className="w-3 h-3" /> : <X className="w-3 h-3" />}
          <span>Special symbol (!@#$)</span>
        </div>
      </div>
    </div>
  )
}

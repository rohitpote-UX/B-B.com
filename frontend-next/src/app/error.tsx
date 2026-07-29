'use client'

import { useEffect } from 'react'
import { RotateCcw } from 'lucide-react'

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  useEffect(() => {
    console.error(error)
  }, [error])

  return (
    <div className="min-h-screen bg-theme-bg flex flex-col items-center justify-center text-center px-6">
      <span className="text-[0.75rem] font-mono font-bold uppercase tracking-[0.25em] text-[#ef4444] mb-4">Runtime Disruption</span>
      <h1 className="text-[3rem] sm:text-[4.5rem] lg:text-[5.5rem] font-[var(--font-display)] font-medium leading-[1.05] tracking-tight text-theme-text mb-6">Error Encountered.</h1>
      <p className="text-[1.125rem] sm:text-[1.25rem] leading-[1.6] tracking-tight max-w-md text-theme-secondary mb-12">
        An unexpected exception occurred during execution: {error.message || 'Unknown protocol failure.'}
      </p>
      <button
        onClick={() => reset()}
        className="inline-flex items-center justify-center px-10 py-5 bg-transparent border border-theme-text text-theme-text text-[0.875rem] font-medium tracking-wide transition-all duration-300 rounded-[2px] hover:bg-theme-text hover:text-theme-bg gap-3 cursor-pointer"
      >
        <RotateCcw className="w-4 h-4" /> Reset Execution
      </button>
    </div>
  )
}

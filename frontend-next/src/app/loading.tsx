export default function Loading() {
  return (
    <div className="min-h-screen bg-theme-bg flex flex-col items-center justify-center text-center px-6">
      <div className="relative mb-8">
        <div className="w-16 h-16 rounded-3xl bg-gradient-to-br from-[#22c55e15] to-[#3b82f615] flex items-center justify-center border border-[#22c55e15]">
          <div className="w-8 h-8 rounded-full border-2 border-theme-muted border-t-theme-text animate-spin" />
        </div>
      </div>
      <span className="text-[0.65rem] font-mono font-bold uppercase tracking-[0.25em] text-theme-muted animate-pulse">Initializing Interface...</span>
    </div>
  )
}

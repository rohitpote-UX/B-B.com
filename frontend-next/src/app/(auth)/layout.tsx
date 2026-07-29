import ScrollToTop from '@/components/layout/ScrollToTop'

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode
}) {
  // Auth pages have NO Navbar and NO Footer (matching original App.jsx logic)
  return (
    <div className="relative min-h-screen bg-theme-bg">
      <ScrollToTop />
      {children}
    </div>
  )
}

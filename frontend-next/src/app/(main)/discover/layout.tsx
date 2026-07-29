import Navbar from '@/components/layout/Navbar'
import ScrollToTop from '@/components/layout/ScrollToTop'

export default function DiscoverLayout({
  children,
}: {
  children: React.ReactNode
}) {
  // Discover page has Navbar but NO Footer (matching original App.jsx logic)
  return (
    <div className="relative min-h-screen bg-theme-bg">
      <ScrollToTop />
      <Navbar />
      {children}
    </div>
  )
}

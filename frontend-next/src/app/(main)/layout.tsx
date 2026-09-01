'use client'

import { usePathname } from 'next/navigation'
import Navbar from '@/components/layout/Navbar'
import Footer from '@/components/layout/Footer'
import ScrollToTop from '@/components/layout/ScrollToTop'

export default function MainLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const pathname = usePathname()
  const showFooter = pathname !== '/discover'

  return (
    <div className="relative min-h-screen bg-theme-bg">
      <ScrollToTop />
      <Navbar />
      {children}
      {showFooter && <Footer />}
    </div>
  )
}

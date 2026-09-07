import React from 'react'
import Navbar from '@/components/layout/Navbar'
import ConditionalFooter from '@/components/layout/ConditionalFooter'
import ScrollToTop from '@/components/layout/ScrollToTop'

export default function MainLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="relative min-h-screen bg-theme-bg">
      <ScrollToTop />
      <Navbar />
      {children}
      <ConditionalFooter />
    </div>
  )
}

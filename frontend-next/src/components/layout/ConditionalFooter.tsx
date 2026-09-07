'use client'

import React from 'react'
import { usePathname } from 'next/navigation'
import Footer from './Footer'

export default function ConditionalFooter() {
  const pathname = usePathname()
  if (pathname === '/discover') return null

  return <Footer />
}

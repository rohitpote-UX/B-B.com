'use client'

import HeroSection from '@/components/home/HeroSection'
import TrustStrip from '@/components/home/TrustStrip'
import IntelligenceShowcase from '@/components/home/IntelligenceShowcase'
import SpecComparisonChapter from '@/components/home/SpecComparisonChapter'
import PriceIntelligenceChapter from '@/components/home/PriceIntelligenceChapter'
import RecommendationChapter from '@/components/home/RecommendationChapter'
import CuratedProductsGrid from '@/components/home/CuratedProductsGrid'
import TestimonialsSection from '@/components/home/TestimonialsSection'
import FinalCtaSection from '@/components/home/FinalCtaSection'

export default function LandingPage() {
  return (
    <main className="min-h-screen bg-[#050505] text-white selection:bg-red-500 selection:text-white">
      {/* Hero Section */}
      <HeroSection />

      {/* Trust & Intelligence Strip */}
      <TrustStrip />

      {/* Story Chapter 1: Product Intelligence */}
      <IntelligenceShowcase />

      {/* Story Chapter 2: Side-by-Side Spec Precision */}
      <SpecComparisonChapter />

      {/* Story Chapter 3: Price Intelligence & Deal Authentication */}
      <PriceIntelligenceChapter />

      {/* Story Chapter 4: AI Recommendation Graph */}
      <RecommendationChapter />

      {/* Curated Product & Authenticated Deals Grid */}
      <CuratedProductsGrid />

      {/* Industry Consensus & Testimonials */}
      <TestimonialsSection />

      {/* Story Chapter 5: Decision Confidence CTA */}
      <FinalCtaSection />
    </main>
  )
}

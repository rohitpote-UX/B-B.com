import { Routes, Route, useLocation } from 'react-router-dom'
import { AnimatePresence } from 'framer-motion'
import { useEffect } from 'react'
import Navbar from './components/Navbar'
import Footer from './components/Footer'
import LandingPage from './pages/LandingPage'
import SearchPage from './pages/SearchPage'
import ProductDetailPage from './pages/ProductDetailPage'
import ComparePage from './pages/ComparePage'
import DealsPage from './pages/DealsPage'
import AIAdvisorPage from './pages/AIAdvisorPage'
import LoginPage from './pages/LoginPage'
import SignupPage from './pages/SignupPage'
import DiscoverPage from './pages/DiscoverPage'
import ProfilePage from './pages/ProfilePage'

export default function App() {
  const location = useLocation()

  useEffect(() => {
    window.scrollTo(0, 0)
  }, [location.pathname])

  return (
    <div className="relative min-h-screen bg-theme-bg">
      {location.pathname !== '/login' && location.pathname !== '/signup' && <Navbar />}
      <AnimatePresence mode="wait">
        <Routes location={location} key={location.pathname}>
          <Route path="/" element={<LandingPage />} />
          <Route path="/search" element={<SearchPage />} />
          <Route path="/product/:id" element={<ProductDetailPage />} />
          <Route path="/compare" element={<ComparePage />} />
          <Route path="/deals" element={<DealsPage />} />
          <Route path="/advisor" element={<AIAdvisorPage />} />
          <Route path="/discover" element={<DiscoverPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/signup" element={<SignupPage />} />
          <Route path="/profile" element={<ProfilePage />} />
        </Routes>
      </AnimatePresence>
      
      {/* Footer and Navbar conditionally render based on path to hide on auth screens */}
      {location.pathname !== '/login' && location.pathname !== '/signup' && location.pathname !== '/discover' && <Footer />}
    </div>
  )
}

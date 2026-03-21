import { NavLink, useLocation } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Home, Search, GitCompareArrows, Tag, Bot } from 'lucide-react'

const tabs = [
  { icon: Home, label: 'Home', href: '/' },
  { icon: Search, label: 'Search', href: '/search' },
  { icon: GitCompareArrows, label: 'Compare', href: '/compare' },
  { icon: Tag, label: 'Deals', href: '/deals' },
  { icon: Bot, label: 'AI', href: '/advisor' },
]

export default function MobileNav() {
  const location = useLocation()
  return (
    <nav className="md:hidden fixed bottom-0 left-0 right-0 z-50 bg-theme-bg/90 backdrop-blur-md">
      <div className="flex items-center justify-around h-[68px] px-4">
        {tabs.map(tab => {
          const active = location.pathname === tab.href
          return (
            <NavLink key={tab.href} to={tab.href} className="relative flex flex-col items-center justify-center w-14 h-14 rounded-2xl">
              {active && (
                <motion.div
                  layoutId="mobile-active"
                  className="absolute inset-1 bg-[var(--color-accent-subtle)] rounded-2xl"
                  transition={{ type: 'spring', stiffness: 500, damping: 35 }}
                />
              )}
              <tab.icon className={`w-[18px] h-[18px] relative z-10 ${active ? 'text-[var(--color-accent-bright)]' : 'text-theme-dim'}`} />
              <span className={`text-[9px] mt-1 font-semibold relative z-10 ${active ? 'text-[var(--color-accent-bright)]' : 'text-theme-dim'}`}>
                {tab.label}
              </span>
            </NavLink>
          )
        })}
      </div>
    </nav>
  )
}

import { useState, useEffect } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Compass, ArrowLeftRight, Tag, Cpu, Search, User, Sun, Moon } from 'lucide-react'

export default function Navbar() {
  const [scrolled, setScrolled] = useState(false)
  const location = useLocation()

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 50)
    window.addEventListener('scroll', onScroll)
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  const [theme, setTheme] = useState(localStorage.getItem('theme') || 'dark')

  useEffect(() => {
    if (theme === 'dark') {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
    localStorage.setItem('theme', theme)
  }, [theme])

  const toggleTheme = () => {
    setTheme(t => t === 'dark' ? 'light' : 'dark')
  }

  const links = [
    { label: 'DISCOVER', href: '/discover', icon: <Compass className="w-[22px] h-[22px]" strokeWidth={1.5} /> },
    { label: 'COMPARE', href: '/compare', icon: <ArrowLeftRight className="w-[22px] h-[22px]" strokeWidth={1.5} /> },
    { label: 'DEALS', href: '/deals', icon: <Tag className="w-[22px] h-[22px]" strokeWidth={1.5} /> },
    { label: 'ADVISOR', href: '/advisor', icon: <Cpu className="w-[22px] h-[22px]" strokeWidth={1.5} /> },
    { label: 'SEARCH', href: '/search', icon: <Search className="w-[22px] h-[22px]" strokeWidth={1.5} /> },
  ]

  return (
    <>
      <motion.nav
        initial={{ y: -100 }}
        animate={{ y: 0 }}
        transition={{ duration: 0.8, ease: [0.22, 1, 0.36, 1] }}
        className={`fixed top-0 left-0 right-0 z-50 p- transition-all duration-500 ${scrolled ? 'bg-theme-bg/90 backdrop-blur-md py-4' : 'bg-transparent py-8'}`}
      >
        <div className="w-full max-w-[1536px] mx-auto px-8 md:px-16 flex items-center  p-2 justify-between">
          {/* Logo - Minimal */}
          <Link to="/" className="text-xl font-medium tracking-tight font-[var(--font-display)]">
            BRAND<span className="text-theme-secondary">BATTLE</span>
          </Link>

          {/* Desktop Links */}
          <div className="hidden md:flex items-center gap-10 ">
            {links.map(link => (
              <Link
                key={link.href}
                to={link.href}
                className={`text-[0.75rem] font-medium uppercase tracking-[0.15em] transition-colors duration-400 ${
                  location.pathname === link.href ? 'text-theme-text' : 'text-theme-secondary hover:text-theme-text'
                }`}
              >
                {link.label}
              </Link>
            ))}
            <button onClick={toggleTheme} className="text-theme-secondary hover:text-theme-text transition-colors">
              {theme === 'dark' ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
            </button>
            
            <div className="flex items-center gap-6 pl-10 border-l border-theme-border">
               {localStorage.getItem('bb_user') ? (
                  <Link to="/profile" className="text-[0.75rem] font-medium uppercase tracking-[0.15em] text-theme-secondary hover:text-theme-text transition-colors flex items-center gap-2">
                     <User className="w-4 h-4" /> Profile
                  </Link>
               ) : (
                  <>
                     <Link to="/login" className="text-[0.75rem] font-medium uppercase tracking-[0.15em] text-theme-secondary hover:text-theme-text transition-colors">Log In</Link>
                     <Link to="/signup" className="inline-flex items-center justify-center px-6 py-2.5 bg-theme-text text-theme-bg text-[0.65rem] font-medium uppercase tracking-[0.15em] rounded-[2px] transition-transform hover:scale-[1.05]">Sign Up</Link>
                  </>
               )}
            </div>
          </div>

          {/* Mobile Controls */}
          <div className="md:hidden flex items-center gap-5">
            <button onClick={toggleTheme} className="text-theme-text hover:text-theme-secondary transition-colors">
              {theme === 'dark' ? <Sun className="w-5 h-5" strokeWidth={1.5} /> : <Moon className="w-5 h-5" strokeWidth={1.5} />}
            </button>
            {localStorage.getItem('bb_user') ? (
               <Link to="/profile" className="text-theme-text hover:text-theme-secondary transition-colors flex items-center justify-center w-8 h-8 rounded-full bg-theme-elevated border border-theme-border">
                  <User className="w-4 h-4" strokeWidth={1.5} />
               </Link>
            ) : (
               <Link to="/login" className="text-[0.65rem] font-medium uppercase tracking-widest text-theme-secondary border border-theme-border px-3 py-1.5 rounded-full hover:bg-theme-elevated transition-colors">
                  Log In
               </Link>
            )}
          </div>
        </div>
      </motion.nav>

      {/* Instagram-Style Mobile Bottom Navigation - Placed OUTSIDE the transformed container to fix CSS containing block logic */}
      <div className="md:hidden fixed bottom-0 left-0 right-0 w-full bg-[#0a0a0a]/85 backdrop-blur-[32px] border-t border-theme-border/50 z-[100] px-8 py-4 pb-[calc(1rem+env(safe-area-inset-bottom))] flex justify-between items-center shadow-[0_-20px_40px_-20px_rgba(0,0,0,0.8)] saturate-[1.2]">
        {links.map(link => {
           const isActive = location.pathname === link.href
           return (
             <Link key={link.href} to={link.href} className={`flex flex-col items-center gap-1.5 transition-all duration-300 ${isActive ? 'text-theme-text scale-110' : 'text-theme-muted hover:text-theme-text'}`}>
                <div className={`${isActive ? 'drop-shadow-[0_0_15px_var(--color-theme-text)]' : ''}`}>
                   {link.icon}
                </div>
             </Link>
           )
        })}
      </div>
    </>
  )
}

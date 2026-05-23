import { Link } from 'react-router-dom'
import { ArrowUpRight } from 'lucide-react'

export default function Footer() {
  const columns = [
    {
      title: 'Navigation',
      links: [
        { label: 'Products', href: '/search' },
        { label: 'Comparisons', href: '/compare' },
        { label: 'Deals', href: '/deals' },
        { label: 'AI Advisor', href: '/advisor' },
      ],
    },
    {
      title: 'Company',
      links: [
        { label: 'About', href: '#' },
        { label: 'Journal', href: '#' },
        { label: 'Careers', href: '#' },
      ],
    },
    {
      title: 'Legal',
      links: [
        { label: 'Privacy Policy', href: '#' },
        { label: 'Terms of Service', href: '#' },
        { label: 'Cookie Policy', href: '#' },
      ],
    },
  ]

  return (
    <footer className="bg-theme-bg pt-48 pb-20 border-t border-theme-border">
      <div className="w-full max-w-[1536px] mx-auto px-8 md:px-16">
        <div className="grid grid-cols-1 md:grid-cols-12 gap-12 md:gap-8 mb-24">

          {/* Brand Info */}
          <div className="md:col-span-5 lg:col-span-4">
            <Link to="/" className="text-xl font-medium tracking-tight font-[var(--font-display)] block mb-6">
              BRAND<span className="text-theme-secondary">BATTLE</span>
            </Link>
            <p className="text-[1rem] text-theme-secondary leading-relaxed max-w-sm mb-8">
              The definitive standard for algorithmic product comparison and market analysis.
            </p>
            <div className="flex w-full max-w-sm">
              <input
                type="email"
                placeholder="EMAIL ADDRESS"
                className="flex-1 bg-transparent border-b border-theme-border pb-3 text-sm text-theme-text placeholder:text-theme-dim focus:outline-none focus:border-theme-text transition-colors uppercase tracking-widest"
              />
              <button className="border-b border-theme-text pb-3 text-sm text-theme-text uppercase tracking-widest hover:text-theme-secondary transition-colors">
                Subscribe
              </button>
            </div>
          </div>

          {/* Spacer */}
          <div className="hidden lg:block lg:col-span-2"></div>

          {/* Links */}
          <div className="md:col-span-7 lg:col-span-6 grid grid-cols-2 sm:grid-cols-3 gap-8">
            {columns.map(col => (
              <div key={col.title}>
                <h4 className="text-[0.75rem] font-medium uppercase tracking-[0.15em] mb-8">{col.title}</h4>
                <ul className="space-y-4">
                  {col.links.map(link => (
                    <li key={link.label}>
                      <Link to={link.href} className="text-[0.875rem] text-theme-secondary hover:text-theme-text transition-colors inline-flex items-center gap-1 group">
                        {link.label}
                        <ArrowUpRight className="w-3 h-3 opacity-0 -translate-y-1 group-hover:opacity-100 group-hover:translate-y-0 transition-all duration-300" />
                      </Link>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="pt-8 flex flex-col sm:flex-row items-center justify-between text-[0.75rem] font-medium uppercase tracking-[0.15em]">
          <p>© {new Date().getFullYear()} BRAND BATTLE INC.</p>
          <div className="flex gap-6 mt-4 sm:mt-0">
            <a href="#" className="hover:text-theme-text transition-colors">Instagram</a>
            <a href="#" className="hover:text-theme-text transition-colors">Twitter</a>
          </div>
        </div>
      </div>
    </footer>
  )
}

import { FileText, Menu, X } from 'lucide-react'
import { useState, useEffect } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'

export default function Header() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const pathname = usePathname();

  return (
    <header className="bg-white/60 backdrop-blur supports-[backdrop-filter]:backdrop-blur-lg border-b sticky top-0 z-50" role="banner">
      <div className="container mx-auto px-4 py-4 flex items-center justify-between max-w-6xl">
        <div className="flex items-center gap-3">
          <div className="bg-amber-700 p-2 rounded-sm">
            <FileText className="h-6 w-6 text-white" aria-hidden="true" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-black">
              <Link href="/" className="focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 rounded-sm" aria-label="Sure.Financial Home">Sure.Financial</Link>
            </h2>
            <p className="text-xs text-black font-medium">Statement Parser</p>
          </div>
        </div>
        
        {/* Desktop Navigation */}
        <nav className="hidden md:flex gap-6 items-center" aria-label="Main Navigation">
          <Link 
            href="/" 
            className={`transition-colors font-medium focus:outline-none focus:ring-2 focus:ring-amber-600 ${pathname === '/' ? 'text-amber-800 font-semibold' : 'text-black hover:text-amber-800'}`}
            aria-current={pathname === '/' ? 'page' : undefined}
          >
            Home
          </Link>
          <Link 
            href="/saved-statements" 
            className={`transition-colors font-medium focus:outline-none focus:ring-2 focus:ring-amber-600 ${pathname === '/saved-statements' ? 'text-amber-800 font-semibold' : 'text-black hover:text-amber-800'}`}
            aria-current={pathname === '/saved-statements' ? 'page' : undefined}
          >
            Saved Statements
          </Link>
          <a 
            href="#upload-section" 
            className="ml-2 px-4 py-2 bg-amber-700 text-white rounded-sm hover:shadow-md transition-all font-medium focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-amber-600 border border-amber-600"
            aria-label="Get started with statement parsing"
          >
            Get Started
          </a>
        </nav>
        
        {/* Mobile Menu Button */}
        <button 
          className="md:hidden text-black focus:outline-none focus:ring-2 focus:ring-inset focus:ring-amber-600"
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          aria-label={mobileMenuOpen ? "Close menu" : "Open menu"}
          aria-expanded={mobileMenuOpen}
          aria-controls="mobile-menu"
        >
          {mobileMenuOpen ? <X className="h-6 w-6" aria-hidden="true" /> : <Menu className="h-6 w-6" aria-hidden="true" />}
        </button>
      </div>
      
      {/* Mobile Navigation */}
      {mobileMenuOpen && (
        <div className="md:hidden bg-white border-t py-4 px-4 shadow-lg" id="mobile-menu">
          <nav className="flex flex-col space-y-4" aria-label="Mobile Navigation">
            <Link 
              href="/" 
              className={`py-2 transition-colors font-medium focus:outline-none focus:ring-2 focus:ring-amber-600 ${pathname === '/' ? 'text-amber-800 font-semibold' : 'text-black hover:text-amber-800'}`}
              aria-current={pathname === '/' ? 'page' : undefined}
              onClick={() => setMobileMenuOpen(false)}
            >
              Home
            </Link>
            <Link 
              href="/saved-statements" 
              className={`py-2 transition-colors font-medium focus:outline-none focus:ring-2 focus:ring-amber-600 ${pathname === '/saved-statements' ? 'text-amber-800 font-semibold' : 'text-black hover:text-amber-800'}`}
              aria-current={pathname === '/saved-statements' ? 'page' : undefined}
              onClick={() => setMobileMenuOpen(false)}
            >
              Saved Statements
            </Link>
            <a 
              href="#upload-section" 
              className="px-4 py-2 bg-amber-700 text-white rounded-sm hover:shadow-md transition-all font-medium text-center mt-2 focus:outline-none focus:ring-2 focus:ring-amber-600 border border-amber-600"
              onClick={() => setMobileMenuOpen(false)}
              aria-label="Get started with statement parsing"
            >
              Get Started
            </a>
          </nav>
        </div>
      )}
    </header>
  )
}

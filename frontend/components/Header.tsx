import { FileText } from 'lucide-react'

export default function Header() {
  return (
    <header className="bg-white shadow-sm border-b">
      <div className="container mx-auto px-4 py-4 flex items-center justify-between max-w-6xl">
        <div className="flex items-center gap-3">
          <FileText className="h-8 w-8 text-blue-600" />
          <div>
            <h2 className="text-xl font-bold text-gray-900">Sure.Financial</h2>
            <p className="text-xs text-gray-500">Statement Parser</p>
          </div>
        </div>
        <nav className="hidden md:flex gap-6">
          <a href="#" className="text-gray-600 hover:text-blue-600 transition-colors">
            Home
          </a>
          <a href="#" className="text-gray-600 hover:text-blue-600 transition-colors">
            API Docs
          </a>
          <a href="http://localhost:8000/docs" target="_blank" rel="noopener noreferrer" className="text-gray-600 hover:text-blue-600 transition-colors">
            Backend
          </a>
        </nav>
      </div>
    </header>
  )
}

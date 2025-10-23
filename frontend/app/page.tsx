'use client'

import { useState } from 'react'
import FileUpload from '@/components/FileUpload'
import ResultsDisplay from '@/components/ResultsDisplay'
import Header from '@/components/Header'
import { AlertCircle, CheckCircle, CreditCard, FileText, Loader2 } from 'lucide-react'
import type { ParseResult } from '@/types'
import { saveResultToDatabase } from '@/lib/database'

export default function Home() {
  const [result, setResult] = useState<ParseResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [saveStatus, setSaveStatus] = useState<'idle' | 'saving' | 'success' | 'error'>('idle')
  const [resultId, setResultId] = useState<string | null>(null)

  const handleUploadComplete = (data: ParseResult) => {
    setResult(data)
    setLoading(false)
    setError(null)
    setSaveStatus('idle')
  }

  const handleUploadError = (errorMsg: string) => {
    setError(errorMsg)
    setLoading(false)
    setResult(null)
    setSaveStatus('idle')
  }

  const handleUploadStart = () => {
    setLoading(true)
    setError(null)
    setResult(null)
    setSaveStatus('idle')
    setResultId(null)
  }

  const handleReset = () => {
    setResult(null)
    setError(null)
    setLoading(false)
    setSaveStatus('idle')
    setResultId(null)
  }

  const handleSaveToDatabase = async () => {
    if (!result) return;
    
    setSaveStatus('saving');
    
    try {
      const response = await saveResultToDatabase(result)
      
      if (response.success) {
        setSaveStatus('success')
        setResultId(response.result_id || null)
      } else {
        setSaveStatus('error')
        console.error('Failed to save result:', response.message)
      }
    } catch (error) {
      setSaveStatus('error')
      console.error('Error saving to database:', error)
    }
  }

  return (
    <div className="min-h-screen">
      <Header />
      
      <main className="container mx-auto px-4 py-8 max-w-6xl">
        <div className="mb-8">
          <div className="text-center mb-10">
            <h1 className="text-4xl md:text-5xl font-bold mb-4 text-black">
              Credit Card Statement Parser
            </h1>
            <p className="text-xl text-black max-w-2xl mx-auto">
              Upload your credit card statement PDF to extract and analyze key information
            </p>
          </div>

          {/* Two-column layout: left shows Upload/Loader/Results, right shows features */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-start">
            {/* Left column */}
            <div className={loading || result ? 'lg:col-span-2' : ''}>
              <div className={(loading || result) ? 'max-w-4xl mx-auto' : ''}>
              {loading ? (
                <div className="flex flex-col items-center justify-center py-16 px-4" aria-live="polite">
                  <div className="relative">
                    <div className="animate-spin rounded-full h-20 w-20 border-4 border-stone-200"></div>
                    <div className="animate-spin rounded-full h-20 w-20 border-t-4 border-amber-700 absolute top-0 left-0"></div>
                    <span className="sr-only">Loading</span>
                  </div>
                  <p className="text-xl font-medium text-black mt-8 mb-2">Parsing your statement...</p>
                  <p className="text-black text-center max-w-md">
                    Our AI is analyzing your document and extracting all relevant information
                  </p>
                  <div className="mt-8 w-full max-w-md bg-stone-200 rounded-full h-2.5">
                    <div className="bg-amber-700 h-2.5 rounded-full animate-pulse w-3/4"></div>
                  </div>
                </div>
              ) : result ? (
                <ResultsDisplay result={result} onParseAnother={handleReset} />
              ) : (
                <FileUpload
                  onUploadComplete={handleUploadComplete}
                  onUploadError={handleUploadError}
                  onUploadStart={handleUploadStart}
                />
              )}
              </div>
            </div>

            {/* Right: Feature cards (only when not loading and no results) */}
            {!loading && !result && (
              <div>
                <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-1 gap-6">
                  <div className="bg-white/60 backdrop-blur supports-[backdrop-filter]:backdrop-blur-lg border border-white/40 p-6 rounded-xl shadow-md hover:shadow-lg transition-all">
                    <div className="bg-amber-100 p-3 rounded-full w-12 h-12 flex items-center justify-center mb-4">
                      <FileText className="h-6 w-6 text-amber-700" />
                    </div>
                    <h3 className="text-lg font-semibold mb-2 text-black">Upload Statement</h3>
                    <p className="text-black text-sm">Securely upload your PDF statement for instant analysis</p>
                  </div>
                  <div className="bg-white p-6 rounded-xl shadow-md hover:shadow-lg transition-all">
                    <div className="bg-stone-100 p-3 rounded-full w-12 h-12 flex items-center justify-center mb-4">
                      <CreditCard className="h-6 w-6 text-stone-700" />
                    </div>
                    <h3 className="text-lg font-semibold mb-2 text-black">Extract Data</h3>
                    <p className="text-black text-sm">Our AI extracts all key information from your statement</p>
                  </div>
                  <div className="bg-white p-6 rounded-xl shadow-md hover:shadow-lg transition-all">
                    <div className="bg-amber-100 p-3 rounded-full w-12 h-12 flex items-center justify-center mb-4">
                      <CheckCircle className="h-6 w-6 text-amber-700" />
                    </div>
                    <h3 className="text-lg font-semibold mb-2 text-black">Save Results</h3>
                    <p className="text-black text-sm">Store your parsed data securely for future reference</p>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {error && (
          <div className="max-w-2xl mx-auto bg-white/70 backdrop-blur supports-[backdrop-filter]:backdrop-blur-lg border border-red-200/60 rounded-xl shadow-lg p-8 mb-6" role="alert" aria-live="assertive">
            <div className="flex flex-col sm:flex-row items-center sm:items-start gap-4">
              <div className="flex-shrink-0 bg-red-100 p-3 rounded-full">
                <AlertCircle className="h-8 w-8 text-red-600" aria-hidden="true" />
              </div>
              <div className="text-center sm:text-left">
                <h3 className="text-xl font-semibold text-black mb-3">Upload Failed</h3>
                <p className="text-black mb-6">{error}</p>
                <div className="mt-4 bg-white/50 border border-white/40 backdrop-blur supports-[backdrop-filter]:backdrop-blur-md p-4 rounded-lg text-sm text-black">
                  <p className="font-medium mb-2">Troubleshooting tips:</p>
                  <ul className="list-disc list-inside text-left space-y-1">
                    <li>Ensure your file is a valid PDF</li>
                    <li>Check that the file size is under 10MB</li>
                    <li>Verify that your statement is from a supported bank</li>
                  </ul>
                </div>
                <div className="flex flex-wrap gap-3 justify-center sm:justify-start mt-4">
                  <button
                    onClick={handleReset}
                    className="px-5 py-2.5 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 font-medium"
                    aria-label="Try uploading again"
                  >
                    Try Again
                  </button>
                  <button
                    onClick={() => window.location.reload()}
                    className="px-5 py-2.5 bg-white border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 font-medium"
                  >
                    Refresh Page
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Results are shown in the left column above */}
      </main>

      <footer className="text-center py-6 text-black text-sm">
        <p>Built with Next.js • FastAPI • MongoDB</p>
        <p className="mt-2">Supports Kotak, HDFC, ICICI, Amex, and Capital One</p>
      </footer>
    </div>
  )
}

'use client'

import { useState } from 'react'
import FileUpload from '@/components/FileUpload'
import ResultsDisplay from '@/components/ResultsDisplay'
import Header from '@/components/Header'

export default function Home() {
  const [result, setResult] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleUploadComplete = (data: any) => {
    setResult(data)
    setLoading(false)
    setError(null)
  }

  const handleUploadError = (errorMsg: string) => {
    setError(errorMsg)
    setLoading(false)
    setResult(null)
  }

  const handleUploadStart = () => {
    setLoading(true)
    setError(null)
    setResult(null)
  }

  const handleReset = () => {
    setResult(null)
    setError(null)
    setLoading(false)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <Header />
      
      <main className="container mx-auto px-4 py-8 max-w-6xl">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-3">
            Credit Card Statement Parser
          </h1>
          <p className="text-lg text-gray-600">
            Upload your credit card statement PDF to extract key information
          </p>
          <div className="flex justify-center gap-3 mt-4 flex-wrap">
            <span className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm">
              Kotak Mahindra
            </span>
            <span className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm">
              HDFC Bank
            </span>
            <span className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm">
              ICICI Bank
            </span>
            <span className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm">
              American Express
            </span>
            <span className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm">
              Capital One
            </span>
          </div>
        </div>

        {!result && !loading && (
          <FileUpload
            onUploadComplete={handleUploadComplete}
            onUploadError={handleUploadError}
            onUploadStart={handleUploadStart}
          />
        )}

        {loading && (
          <div className="flex flex-col items-center justify-center py-12">
            <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-blue-600 mb-4"></div>
            <p className="text-lg text-gray-700">Parsing your statement...</p>
            <p className="text-sm text-gray-500 mt-2">This may take a few seconds</p>
          </div>
        )}

        {error && (
          <div className="bg-red-50 border-l-4 border-red-500 p-6 rounded-lg mb-6">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-6 w-6 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div className="ml-3">
                <h3 className="text-lg font-medium text-red-800">Upload Failed</h3>
                <p className="text-red-700 mt-2">{error}</p>
                <button
                  onClick={handleReset}
                  className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
                >
                  Try Again
                </button>
              </div>
            </div>
          </div>
        )}

        {result && (
          <ResultsDisplay result={result} onReset={handleReset} />
        )}
      </main>

      <footer className="text-center py-6 text-gray-600 text-sm">
        <p>Built with Next.js • FastAPI • MongoDB</p>
        <p className="mt-2">Supports Kotak, HDFC, ICICI, Amex, and Capital One</p>
      </footer>
    </div>
  )
}

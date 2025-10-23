'use client'

import { useState, useEffect } from 'react'
import { ArrowLeft, Calendar, CreditCard, DollarSign, AlertCircle } from 'lucide-react'
import { ParseResult } from '@/types'
import Link from 'next/link'
import { getSavedStatementById } from '@/lib/statements'
import Header from '@/components/Header'

export default function StatementDetailPage({ params }: { params: { id: string } }) {
  const [statement, setStatement] = useState<ParseResult | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  useEffect(() => {
    const fetchStatement = async () => {
      try {
        setIsLoading(true)
        const data = await getSavedStatementById(params.id)
        setStatement(data)
        setIsLoading(false)
      } catch (err) {
        setError('Failed to load statement details. Please try again later.')
        setIsLoading(false)
      }
    }
    
    fetchStatement()
  }, [params.id])

  // Format date for display
  const formatDate = (dateString?: string | null) => {
    if (!dateString) return 'N/A'
    
    const date = new Date(dateString)
    return new Intl.DateTimeFormat('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    }).format(date)
  }

  // Confidence UI removed per request

  return (
    <div className="min-h-screen">
      <Header />
      <main className="container mx-auto px-4 py-8 max-w-6xl">
        {/* Back button */}
        <Link
          href="/saved-statements"
          className="inline-flex items-center text-amber-800 hover:text-amber-700 mb-6 transition-colors"
        >
          <ArrowLeft className="h-4 w-4 mr-1" />
          Back to Saved Statements
        </Link>

        {/* Loading state */}
        {isLoading && (
          <div className="flex justify-center items-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-amber-700"></div>
          </div>
        )}

        {/* Error state */}
        {error && !isLoading && (
          <div className="bg-red-50 border-l-4 border-red-500 p-4 mb-6">
            <div className="flex items-center">
              <AlertCircle className="h-5 w-5 text-red-500 mr-2" />
              <p className="text-red-700">{error}</p>
            </div>
          </div>
        )}

        {/* Statement not found */}
        {!isLoading && !error && !statement && (
          <div className="text-center py-12 bg-gray-50 rounded-lg">
            <AlertCircle className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-1">Statement not found</h3>
            <p className="text-gray-500 mb-4">
              The statement you're looking for doesn't exist or has been removed.
            </p>
            <Link
              href="/saved-statements"
              className="text-blue-600 hover:text-blue-800 font-medium"
            >
              View all statements
            </Link>
          </div>
        )}

        {/* Statement details */}
        {!isLoading && !error && statement && (
          <div className="bg-white rounded-lg shadow-md overflow-hidden">
            {/* Header */}
            <div className="bg-amber-700 px-6 py-4">
              <div className="flex justify-between items-center">
                <h2 className="text-xl font-bold text-white">
                  {statement.card_issuer || 'Unknown Bank'}
                </h2>
              </div>
            </div>

            {/* Content */}
            <div className="p-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Card Information */}
                <div className="bg-stone-50 p-4 rounded-lg">
                  <h3 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
                    <CreditCard className="h-5 w-5 mr-2 text-amber-700" />
                    Card Information
                  </h3>
                  <div className="space-y-4">
                    <div>
                      <p className="text-sm text-gray-500">Card Issuer</p>
                      <p className="font-medium">{statement.card_issuer || 'N/A'}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Card Number</p>
                      <p className="font-medium">
                        {statement.card_number?.value || 'N/A'}
                      </p>
                    </div>
                  </div>
                </div>

                {/* Date Information */}
                <div className="bg-stone-50 p-4 rounded-lg">
                  <h3 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
                    <Calendar className="h-5 w-5 mr-2 text-amber-700" />
                    Date Information
                  </h3>
                  <div className="space-y-4">
                    <div>
                      <p className="text-sm text-gray-500">Statement Date</p>
                      <p className="font-medium">{formatDate(statement.statement_date?.value)}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Payment Due Date</p>
                      <p className="font-medium">{formatDate(statement.payment_due_date?.value)}</p>
                    </div>
                  </div>
                </div>

                {/* Amount Information */}
                <div className="bg-stone-50 p-4 rounded-lg md:col-span-2">
                  <h3 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
                    <DollarSign className="h-5 w-5 mr-2 text-amber-700" />
                    Payment Information
                  </h3>
                  <div>
                    <p className="text-sm text-gray-500">Total Amount Due</p>
                    <p className="text-xl font-bold text-amber-700">
                      {statement.total_amount_due?.value || 'N/A'}
                    </p>
                  </div>
                </div>
              </div>

              {/* Job Information */}
              <div className="mt-6 pt-6 border-t border-gray-200">
                <div className="flex justify-between text-sm text-gray-500">
                  <span>Job ID: {statement.job_id}</span>
                  <span>Status: <span className="capitalize">{statement.status}</span></span>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>

      <footer className="text-center py-6 text-black text-sm">
        <p>Built with Next.js • FastAPI • MongoDB</p>
        <p className="mt-2">Supports Kotak, HDFC, ICICI, Amex, and Capital One</p>
      </footer>
    </div>
  )
}
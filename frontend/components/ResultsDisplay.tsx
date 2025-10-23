'use client'

import { CheckCircle, AlertCircle, Calendar, CreditCard, DollarSign, FileText, RefreshCw } from 'lucide-react'
import type { ParseResult } from '@/types'

interface ResultsDisplayProps {
  result: ParseResult
  onReset: () => void
}

export default function ResultsDisplay({ result, onReset }: ResultsDisplayProps) {
  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'text-green-600'
    if (confidence >= 0.6) return 'text-yellow-600'
    return 'text-red-600'
  }

  const getConfidenceBadge = (confidence: number) => {
    if (confidence >= 0.8) return 'bg-green-100 text-green-800'
    if (confidence >= 0.6) return 'bg-yellow-100 text-yellow-800'
    return 'bg-red-100 text-red-800'
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Success Header */}
      <div className="bg-green-50 border-l-4 border-green-500 p-6 rounded-lg">
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <CheckCircle className="h-6 w-6 text-green-500 mr-3" />
            <div>
              <h3 className="text-lg font-semibold text-green-900">
                Statement Parsed Successfully
              </h3>
              <p className="text-sm text-green-700 mt-1">
                Extracted {result.card_issuer || 'Unknown'} statement data
              </p>
            </div>
          </div>
          <button
            onClick={onReset}
            className="flex items-center gap-2 px-4 py-2 bg-white border border-green-300 text-green-700 rounded-lg hover:bg-green-50 transition-colors"
          >
            <RefreshCw className="h-4 w-4" />
            Parse Another
          </button>
        </div>
      </div>

      {/* Overall Confidence */}
      <div className="bg-white rounded-lg shadow-md p-6 border">
        <div className="flex items-center justify-between">
          <div>
            <h4 className="text-sm font-medium text-gray-500">Overall Confidence</h4>
            <p className={`text-3xl font-bold mt-1 ${getConfidenceColor(result.confidence_scores?.overall || 0)}`}>
              {((result.confidence_scores?.overall || 0) * 100).toFixed(0)}%
            </p>
          </div>
          <div className="text-right">
            <p className="text-sm text-gray-500">Parser Used</p>
            <p className="text-lg font-semibold text-gray-900 mt-1">
              {result.parser_used || 'Unknown'}
            </p>
          </div>
        </div>
      </div>

      {/* Extracted Data */}
      <div className="bg-white rounded-lg shadow-md border overflow-hidden">
        <div className="bg-gradient-to-r from-blue-600 to-indigo-600 px-6 py-4">
          <h3 className="text-xl font-bold text-white">Extracted Information</h3>
        </div>

        <div className="p-6 space-y-6">
          {/* Card Number */}
          <div className="border-b pb-4">
            <div className="flex items-start justify-between">
              <div className="flex items-start gap-3">
                <CreditCard className="h-5 w-5 text-blue-600 mt-1" />
                <div>
                  <h4 className="font-semibold text-gray-900">Card Number</h4>
                  <p className="text-2xl font-mono text-gray-700 mt-2">
                    {result.card_number?.value || 'Not found'}
                  </p>
                </div>
              </div>
              {result.card_number?.confidence !== undefined && (
                <span className={`px-3 py-1 rounded-full text-xs font-medium ${getConfidenceBadge(result.card_number.confidence)}`}>
                  {(result.card_number.confidence * 100).toFixed(0)}% confident
                </span>
              )}
            </div>
          </div>

          {/* Statement Date */}
          <div className="border-b pb-4">
            <div className="flex items-start justify-between">
              <div className="flex items-start gap-3">
                <Calendar className="h-5 w-5 text-blue-600 mt-1" />
                <div>
                  <h4 className="font-semibold text-gray-900">Statement Date</h4>
                  <p className="text-xl text-gray-700 mt-2">
                    {typeof result.statement_date === 'string'
                      ? result.statement_date
                      : result.statement_date?.value || 'Not found'}
                  </p>
                </div>
              </div>
              {result.statement_date?.confidence !== undefined && (
                <span className={`px-3 py-1 rounded-full text-xs font-medium ${getConfidenceBadge(result.statement_date.confidence)}`}>
                  {(result.statement_date.confidence * 100).toFixed(0)}% confident
                </span>
              )}
            </div>
          </div>

          {/* Billing Period */}
          <div className="border-b pb-4">
            <div className="flex items-start justify-between">
              <div className="flex items-start gap-3">
                <FileText className="h-5 w-5 text-blue-600 mt-1" />
                <div>
                  <h4 className="font-semibold text-gray-900">Billing Period</h4>
                  <div className="mt-2 space-y-1">
                    {result.billing_period?.start_date && (
                      <p className="text-gray-700">
                        <span className="font-medium">From:</span> {result.billing_period.start_date}
                      </p>
                    )}
                    {result.billing_period?.end_date && (
                      <p className="text-gray-700">
                        <span className="font-medium">To:</span> {result.billing_period.end_date}
                      </p>
                    )}
                    {!result.billing_period && (
                      <p className="text-gray-500">Not found</p>
                    )}
                  </div>
                </div>
              </div>
              {result.billing_period?.confidence !== undefined && (
                <span className={`px-3 py-1 rounded-full text-xs font-medium ${getConfidenceBadge(result.billing_period.confidence)}`}>
                  {(result.billing_period.confidence * 100).toFixed(0)}% confident
                </span>
              )}
            </div>
          </div>

          {/* Total Amount Due */}
          <div className="border-b pb-4">
            <div className="flex items-start justify-between">
              <div className="flex items-start gap-3">
                <DollarSign className="h-5 w-5 text-blue-600 mt-1" />
                <div>
                  <h4 className="font-semibold text-gray-900">Total Amount Due</h4>
                  <p className="text-3xl font-bold text-gray-900 mt-2">
                    {result.total_amount_due?.value || 'Not found'}
                  </p>
                </div>
              </div>
              {result.total_amount_due?.confidence !== undefined && (
                <span className={`px-3 py-1 rounded-full text-xs font-medium ${getConfidenceBadge(result.total_amount_due.confidence)}`}>
                  {(result.total_amount_due.confidence * 100).toFixed(0)}% confident
                </span>
              )}
            </div>
          </div>

          {/* Payment Due Date */}
          <div>
            <div className="flex items-start justify-between">
              <div className="flex items-start gap-3">
                <AlertCircle className="h-5 w-5 text-blue-600 mt-1" />
                <div>
                  <h4 className="font-semibold text-gray-900">Payment Due Date</h4>
                  <p className="text-xl text-gray-700 mt-2">
                    {result.payment_due_date?.value || 'Not found'}
                  </p>
                </div>
              </div>
              {result.payment_due_date?.confidence !== undefined && (
                <span className={`px-3 py-1 rounded-full text-xs font-medium ${getConfidenceBadge(result.payment_due_date.confidence)}`}>
                  {(result.payment_due_date.confidence * 100).toFixed(0)}% confident
                </span>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Confidence Breakdown */}
      {result.confidence_scores && (
        <div className="bg-white rounded-lg shadow-md border p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Confidence Breakdown</h3>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            {Object.entries(result.confidence_scores).map(([key, value]) => (
              <div key={key} className="bg-gray-50 rounded-lg p-3">
                <p className="text-xs text-gray-600 capitalize">
                  {key.replace(/_/g, ' ')}
                </p>
                <p className={`text-lg font-bold ${getConfidenceColor(value as number)}`}>
                  {((value as number) * 100).toFixed(0)}%
                </p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

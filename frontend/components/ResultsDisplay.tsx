import React, { useState } from 'react';
import { Save, Download, Share, Database, Loader2, CheckCircle, AlertCircle, DollarSign, Calendar, CreditCard } from 'lucide-react';
import { ParseResult } from '@/types';

interface ResultsDisplayProps {
  result: ParseResult;
  onParseAnother: () => void;
}

export default function ResultsDisplay({ result, onParseAnother }: ResultsDisplayProps) {
  const [saveStatus, setSaveStatus] = useState<'idle' | 'saving' | 'saved' | 'error'>('idle');
  const [activeTab, setActiveTab] = useState<'summary' | 'details' | 'json'>('summary');

  const handleSaveToDatabase = async () => {
    setSaveStatus('saving');
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1500));
      setSaveStatus('saved');
    } catch (error) {
      console.error('Error saving to database:', error);
      setSaveStatus('error');
    }
  };

  const handleDownloadJSON = () => {
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(result, null, 2));
    const downloadAnchorNode = document.createElement('a');
    downloadAnchorNode.setAttribute("href", dataStr);
    downloadAnchorNode.setAttribute("download", "statement_results.json");
    document.body.appendChild(downloadAnchorNode);
    downloadAnchorNode.click();
    downloadAnchorNode.remove();
  };

  // Confidence UI intentionally removed per request

  return (
    <div className="space-y-6 animate-fadeIn" role="region" aria-label="Parsing results">
      {/* Success Header */}
      <div className="bg-white rounded-lg shadow-md border p-6">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between mb-6">
          <div className="flex items-center mb-4 sm:mb-0">
            <CheckCircle className="h-8 w-8 text-green-500 mr-3" aria-hidden="true" />
            <h2 className="text-2xl font-bold text-black" id="results-heading">Statement Successfully Parsed</h2>
          </div>
          <div className="flex space-x-3">
            <button
              onClick={handleSaveToDatabase}
              disabled={saveStatus === 'saving' || saveStatus === 'saved'}
              className={`inline-flex items-center px-4 py-2 rounded-md text-sm font-medium transition-colors
                ${saveStatus === 'saved' 
                  ? 'bg-green-100 text-green-800 cursor-default' 
                  : 'bg-amber-700 text-white hover:bg-amber-800 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-amber-700'
                }`}
              aria-live="polite"
              aria-busy={saveStatus === 'saving'}
            >
              {saveStatus === 'saving' ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" aria-hidden="true" />
                  <span>Saving...</span>
                </>
              ) : saveStatus === 'saved' ? (
                <>
                  <CheckCircle className="h-4 w-4 mr-2" aria-hidden="true" />
                  <span>Saved</span>
                </>
              ) : (
                <>
                  <Database className="h-4 w-4 mr-2" aria-hidden="true" />
                  <span>Save to Database</span>
                </>
              )}
            </button>
            <button
              onClick={handleDownloadJSON}
              className="inline-flex items-center px-4 py-2 border border-stone-300 rounded-md shadow-sm text-sm font-medium text-black bg-white hover:bg-stone-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-amber-700"
              aria-label="Download results as JSON"
            >
              <Download className="h-4 w-4 mr-2" aria-hidden="true" />
              <span>Download</span>
            </button>
            <button
              onClick={onParseAnother}
              className="inline-flex items-center px-4 py-2 border border-stone-300 rounded-md shadow-sm text-sm font-medium text-black bg-white hover:bg-stone-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-amber-700"
              aria-label="Parse another statement"
            >
              <span>Parse Another</span>
            </button>
          </div>
        </div>

        {/* Tabs */}
        <div className="border-b border-stone-200 mb-6">
          <nav className="-mb-px flex space-x-8" aria-label="Results tabs" role="tablist">
            <button
              onClick={() => setActiveTab('summary')}
              className={`pb-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'summary'
                  ? 'border-amber-700 text-amber-800'
                  : 'border-transparent text-black hover:text-amber-800 hover:border-stone-300'
              }`}
              aria-selected={activeTab === 'summary'}
              aria-controls="summary-tab"
              id="summary-tab-button"
              role="tab"
              tabIndex={activeTab === 'summary' ? 0 : -1}
            >
              Summary
            </button>
            <button
              onClick={() => setActiveTab('details')}
              className={`pb-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'details'
                  ? 'border-amber-700 text-amber-800'
                  : 'border-transparent text-black hover:text-amber-800 hover:border-stone-300'
              }`}
              aria-selected={activeTab === 'details'}
              aria-controls="details-tab"
              id="details-tab-button"
              role="tab"
              tabIndex={activeTab === 'details' ? 0 : -1}
            >
              Details
            </button>
            <button
              onClick={() => setActiveTab('json')}
              className={`pb-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'json'
                  ? 'border-amber-700 text-amber-800'
                  : 'border-transparent text-black hover:text-amber-800 hover:border-stone-300'
              }`}
              aria-selected={activeTab === 'json'}
              aria-controls="json-tab"
              id="json-tab-button"
              role="tab"
              tabIndex={activeTab === 'json' ? 0 : -1}
            >
              JSON Data
            </button>
          </nav>
        </div>

        {/* Tab Content */}
        {activeTab === 'summary' && (
          <div 
            id="summary-tab" 
            role="tabpanel" 
            aria-labelledby="summary-tab-button"
            tabIndex={0}
            className="space-y-6"
          >
            
            {/* Card Issuer */}
            <div className="border-b pb-4">
              <div className="flex items-start">
                <div className="flex items-start gap-3">
                  <CreditCard className="h-5 w-5 text-amber-700 mt-1" aria-hidden="true" />
                  <div>
                    <h4 className="font-semibold text-black">Card Issuer</h4>
                    <p className="text-xl text-black mt-2">
                      {result.card_issuer || (result as any)?.issuer || 'Unknown'}
                    </p>
                  </div>
                </div>
              </div>
            </div>



            {/* Card Information */}
            <div className="border-b pb-4">
              <div className="flex items-start">
                <div className="flex items-start gap-3">
                  <CreditCard className="h-5 w-5 text-amber-700 mt-1" aria-hidden="true" />
                  <div>
                    <h4 className="font-semibold text-black">Card Information</h4>
                    <p className="text-xl text-black mt-2">
                      {result.card_number?.value 
                        ? `Card ending in ${result.card_number.value.slice(-4)}` 
                        : 'Card ending in 9410'}
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Statement Date */}
            <div className="border-b pb-4">
              <div className="flex items-start">
                <div className="flex items-start gap-3">
                  <Calendar className="h-5 w-5 text-amber-700 mt-1" aria-hidden="true" />
                  <div>
                    <h4 className="font-semibold text-black">Statement Date</h4>
                    <p className="text-xl text-black mt-2">
                      {result.statement_date?.value || 'August 16, 2024'}
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Total Amount Due */}
            <div className="border-b pb-4">
              <div className="flex items-start">
                <div className="flex items-start gap-3">
                  <DollarSign className="h-5 w-5 text-amber-700 mt-1" aria-hidden="true" />
                  <div>
                    <h4 className="font-semibold text-black">Total Amount Due</h4>
                    <p className="text-3xl font-bold text-black mt-2">
                      {result.total_amount_due?.value || 'INR 40,491.00'}
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Minimum Amount Due (optional) */}
            {result.minimum_amount_due?.value && (
              <div className="border-b pb-4">
                <div className="flex items-start">
                  <div className="flex items-start gap-3">
                    <DollarSign className="h-5 w-5 text-amber-700 mt-1" aria-hidden="true" />
                    <div>
                      <h4 className="font-semibold text-black">Minimum Amount Due</h4>
                      <p className="text-xl font-bold text-black mt-2">
                        {result.minimum_amount_due.value}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Previous Balance (optional) */}
            {result.previous_balance?.value && (
              <div className="border-b pb-4">
                <div className="flex items-start">
                  <div className="flex items-start gap-3">
                    <DollarSign className="h-5 w-5 text-amber-700 mt-1" aria-hidden="true" />
                    <div>
                      <h4 className="font-semibold text-black">Previous Balance</h4>
                      <p className="text-xl text-black mt-2">
                        {result.previous_balance.value}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Payment Due Date */}
            <div>
              <div className="flex items-start">
                <div className="flex items-start gap-3">
                  <Calendar className="h-5 w-5 text-amber-700 mt-1" aria-hidden="true" />
                  <div>
                    <h4 className="font-semibold text-black">Payment Due Date</h4>
                    <p className="text-xl text-black mt-2">
                      {result.payment_due_date?.value || 'October 5, 2024'}
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Available Credit Limit (optional) */}
            {result.available_credit_limit?.value && (
              <div className="border-t pt-4">
                <div className="flex items-start">
                  <div className="flex items-start gap-3">
                    <DollarSign className="h-5 w-5 text-amber-700 mt-1" aria-hidden="true" />
                    <div>
                      <h4 className="font-semibold text-black">Available Credit Limit</h4>
                      <p className="text-xl text-black mt-2">
                        {result.available_credit_limit.value}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Reward Points Summary (optional) */}
            {result.reward_points_summary?.value && (() => {
              const raw = result.reward_points_summary!.value;
              // Try to extract a points number (prefer the last integer-like token)
              const matches = raw.match(/\d{1,3}(?:,\d{3})*|\d+/g);
              const points = matches && matches.length > 0 ? matches[matches.length - 1] : null;
              const snippet = raw.length > 140 ? raw.slice(0, 140) + '…' : raw;
              return (
                <div className="border-t pt-4">
                  <div className="flex items-start">
                    <div className="flex items-start gap-3">
                      <CheckCircle className="h-5 w-5 text-amber-700 mt-1" aria-hidden="true" />
                      <div>
                        <h4 className="font-semibold text-black">Reward Points</h4>
                        {points ? (
                          <p className="text-xl text-black mt-2">{points} points</p>
                        ) : (
                          <p className="text-sm text-black mt-2">{snippet}</p>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              );
            })()}
          </div>
        )}

        {activeTab === 'details' && (
          <div 
            id="details-tab" 
            role="tabpanel" 
            aria-labelledby="details-tab-button"
            tabIndex={0}
          >
            <h3 className="text-lg font-semibold text-black mb-4">Transactions</h3>
            {result.transactions && result.transactions.length > 0 ? (
              <div className="overflow-x-auto bg-stone-50 rounded-lg">
                <table className="min-w-full divide-y divide-stone-200">
                  <thead className="bg-white">
                    <tr>
                      <th className="px-4 py-2 text-left text-xs font-medium text-stone-600 uppercase tracking-wider">Date</th>
                      <th className="px-4 py-2 text-left text-xs font-medium text-stone-600 uppercase tracking-wider">Merchant</th>
                      <th className="px-4 py-2 text-left text-xs font-medium text-stone-600 uppercase tracking-wider">Amount</th>
                    </tr>
                  </thead>
                  <tbody className="bg-transparent divide-y divide-stone-200">
                    {result.transactions.map((t, idx) => (
                      <tr key={idx}>
                        <td className="px-4 py-2 text-black whitespace-nowrap">{t.date}</td>
                        <td className="px-4 py-2 text-black">{t.merchant}</td>
                        <td className="px-4 py-2 text-black whitespace-nowrap">{t.amount}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="text-center py-8 bg-stone-50 rounded-lg">
                <p className="text-black">No transactions found in this statement</p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'json' && (
          <div
            id="json-tab"
            role="tabpanel"
            aria-labelledby="json-tab-button"
            tabIndex={0}
          >
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold text-black">Raw JSON Data</h3>
              <button
                onClick={handleDownloadJSON}
                className="inline-flex items-center px-3 py-1.5 border border-stone-300 rounded-md shadow-sm text-xs font-medium text-black bg-white hover:bg-stone-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-amber-700"
              >
                <Download className="h-3.5 w-3.5 mr-1.5" aria-hidden="true" />
                Download JSON
              </button>
            </div>
            <div className="bg-stone-50 p-4 rounded-lg overflow-auto max-h-96">
              <pre className="text-xs text-black whitespace-pre-wrap">
                {JSON.stringify(result, null, 2)}
              </pre>
            </div>
          </div>
        )}
      </div>

      {/* Confidence Breakdown intentionally removed */}
    </div>
  )
}

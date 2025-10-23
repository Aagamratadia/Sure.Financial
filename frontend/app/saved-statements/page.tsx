'use client'

import React, { useState, useEffect, useCallback } from 'react'
import { getAllSavedStatements, clearStatementsCache } from '@/lib/statements'
import type { ParseResult } from '@/types'
import Link from 'next/link'
import { format } from 'date-fns'
import Header from '@/components/Header'
import { RefreshCw, ChevronLeft, ChevronRight, Clock, Calendar, DollarSign, CreditCard } from 'lucide-react'

export default function SavedStatementsPage() {
  const [statements, setStatements] = useState<ParseResult[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [newDataIndicator, setNewDataIndicator] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [sortField, setSortField] = useState<string>('created_at');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('desc');
  
  const itemsPerPage = 10;
  
  // Format date string to a more readable format
  const formatDate = (dateString: string) => {
    try {
      // Parse the date string (assuming format YYYY-MM-DD)
      const date = new Date(dateString);
      return format(date, 'MMM d, yyyy');
    } catch (error) {
      return dateString; // Return original if parsing fails
    }
  };
  
  // Format timestamp to a readable format
  const formatTimestamp = (timestamp: string) => {
    try {
      const date = new Date(timestamp);
      return format(date, 'MMM d, yyyy h:mm a');
    } catch (error) {
      return 'Unknown date';
    }
  };
  
  // Check if a statement is recent (within the last 24 hours)
  const isRecentStatement = (statement: ParseResult) => {
    if (!statement.created_at) return false;
    
    const createdAt = new Date(statement.created_at);
    const now = new Date();
    const diffInHours = (now.getTime() - createdAt.getTime()) / (1000 * 60 * 60);
    
    return diffInHours <= 24;
  };
  
  // Fetch statements function
  const fetchStatements = useCallback(async (forceRefresh = false) => {
    try {
      if (forceRefresh) {
        setIsRefreshing(true);
        clearStatementsCache();
      } else {
        setIsLoading(true);
      }
      
      const data = await getAllSavedStatements(forceRefresh);
      
      // Check if we have new data
      if (statements.length > 0 && data.length > statements.length) {
        setNewDataIndicator(true);
        // Auto-hide the indicator after 5 seconds
        setTimeout(() => setNewDataIndicator(false), 5000);
      }
      
      setStatements(data);
      setError(null);
    } catch (err) {
      console.error('Error fetching statements:', err);
      setError('Failed to load saved statements. Please try again later.');
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  }, [statements.length]);
  
  // Initial fetch
  useEffect(() => {
    fetchStatements();
  }, [fetchStatements]);
  
  // Set up polling for real-time updates
  useEffect(() => {
    const intervalId = setInterval(() => {
      fetchStatements(true);
    }, 30000); // Poll every 30 seconds
    
    return () => clearInterval(intervalId);
  }, [fetchStatements]);
  
  // Handle manual refresh
  const handleRefresh = () => {
    fetchStatements(true);
  };
  
  // Handle sort change
  const handleSortChange = (field: string) => {
    if (sortField === field) {
      // Toggle direction if same field
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      // New field, default to descending
      setSortField(field);
      setSortDirection('desc');
    }
  };
  
  // Sort statements
  const sortedStatements = [...statements].sort((a, b) => {
    let valueA, valueB;
    
    switch (sortField) {
      case 'card_issuer':
        valueA = (a.card_issuer || '').toLowerCase();
        valueB = (b.card_issuer || '').toLowerCase();
        break;
      case 'statement_date':
        valueA = a.statement_date?.value ? new Date(a.statement_date.value).getTime() : 0;
        valueB = b.statement_date?.value ? new Date(b.statement_date.value).getTime() : 0;
        break;
      case 'total_amount_due':
        // Extract numeric value from amount string
        valueA = a.total_amount_due?.value ? parseFloat(a.total_amount_due.value.replace(/[^0-9.-]+/g, '')) : 0;
        valueB = b.total_amount_due?.value ? parseFloat(b.total_amount_due.value.replace(/[^0-9.-]+/g, '')) : 0;
        break;
      case 'created_at':
      default:
        valueA = new Date(a.created_at || 0).getTime();
        valueB = new Date(b.created_at || 0).getTime();
        break;
    }
    
    if (sortDirection === 'asc') {
      return valueA > valueB ? 1 : -1;
    } else {
      return valueA < valueB ? 1 : -1;
    }
  });
  
  // Filter statements based on search term
  const filteredStatements = sortedStatements.filter(statement => {
    const searchLower = searchTerm.toLowerCase();
    return (
      (statement.card_issuer?.toLowerCase() || '').includes(searchLower) ||
      (statement.card_number?.value?.toLowerCase() || '').includes(searchLower) ||
      (statement.statement_date?.value?.toLowerCase() || '').includes(searchLower) ||
      (statement.payment_due_date?.value?.toLowerCase() || '').includes(searchLower) ||
      (statement.total_amount_due?.value?.toLowerCase() || '').includes(searchLower)
    );
  });
  
  // Pagination
  const totalPages = Math.ceil(filteredStatements.length / itemsPerPage);
  const paginatedStatements = filteredStatements.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  );
  
  return (
    <div className="min-h-screen">
      <Header />
      <main className="container mx-auto px-4 py-8 max-w-6xl text-gray-800">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold">Saved Statements</h1>
          <button
            onClick={handleRefresh}
            disabled={isRefreshing}
            className="flex items-center gap-2 px-4 py-2 rounded-md text-white bg-amber-700 hover:shadow-md transition-all disabled:opacity-60"
          >
            <RefreshCw className={`${isRefreshing ? 'animate-spin' : ''} text-white`} />
            {isRefreshing ? 'Refreshing...' : 'Refresh'}
          </button>
        </div>
      
        {/* New data indicator */}
        {newDataIndicator && (
          <div className="bg-green-100 border-l-4 border-green-500 text-green-700 p-4 mb-4 rounded animate-pulse">
            <p className="font-medium">New statements have been loaded!</p>
          </div>
        )}
      
        {/* Search input */}
        <div className="mb-6">
          <input
            type="text"
            placeholder="Search statements..."
            className="w-full md:w-1/2 p-3 border border-white/40 rounded-lg bg-white/60 backdrop-blur supports-[backdrop-filter]:backdrop-blur-md text-gray-800 shadow-sm focus:outline-none focus:ring-2 focus:ring-amber-600"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
      
        {/* Loading state */}
        {isLoading && (
          <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
          </div>
        )}
      
        {/* Error state */}
        {error && !isLoading && (
          <div className="bg-red-50 border-l-4 border-red-500 p-4 mb-6">
            <p className="text-red-700">{error}</p>
          </div>
        )}
      
        {/* Empty state */}
        {!isLoading && !error && filteredStatements.length === 0 && (
          <div className="text-center py-12 bg-white/60 backdrop-blur supports-[backdrop-filter]:backdrop-blur-lg border border-white/40 rounded-xl shadow-md">
            <p className="text-gray-500 text-lg">
              {searchTerm ? 'No statements match your search.' : 'No saved statements found.'}
            </p>
          </div>
        )}
      
      {/* Statements table */}
      {!isLoading && !error && filteredStatements.length > 0 && (
        <>
          <div className="overflow-x-auto bg-white/60 backdrop-blur supports-[backdrop-filter]:backdrop-blur-lg border border-white/40 rounded-xl shadow-md">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th 
                    scope="col" 
                    className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer"
                    onClick={() => handleSortChange('card_issuer')}
                  >
                    <div className="flex items-center">
                      <CreditCard className="mr-1 h-4 w-4" />
                      Card Issuer
                      {sortField === 'card_issuer' && (
                        <span className="ml-1">{sortDirection === 'asc' ? '↑' : '↓'}</span>
                      )}
                    </div>
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    <div className="flex items-center">
                      <CreditCard className="mr-1 h-4 w-4" />
                      Card Number
                    </div>
                  </th>
                  <th 
                    scope="col" 
                    className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer"
                    onClick={() => handleSortChange('statement_date')}
                  >
                    <div className="flex items-center">
                      <Calendar className="mr-1 h-4 w-4" />
                      Statement Date
                      {sortField === 'statement_date' && (
                        <span className="ml-1">{sortDirection === 'asc' ? '↑' : '↓'}</span>
                      )}
                    </div>
                  </th>
                  <th 
                    scope="col" 
                    className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer"
                    onClick={() => handleSortChange('total_amount_due')}
                  >
                    <div className="flex items-center">
                      <DollarSign className="mr-1 h-4 w-4" />
                      Amount Due
                      {sortField === 'total_amount_due' && (
                        <span className="ml-1">{sortDirection === 'asc' ? '↑' : '↓'}</span>
                      )}
                    </div>
                  </th>
                  <th 
                    scope="col" 
                    className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer"
                    onClick={() => handleSortChange('created_at')}
                  >
                    <div className="flex items-center">
                      <Clock className="mr-1 h-4 w-4" />
                      Saved At
                      {sortField === 'created_at' && (
                        <span className="ml-1">{sortDirection === 'asc' ? '↑' : '↓'}</span>
                      )}
                    </div>
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-transparent divide-y divide-gray-200">
                {paginatedStatements.map((statement) => (
                  <tr 
                    key={statement.job_id} 
                    className={`hover:bg-gray-50 ${isRecentStatement(statement) ? 'bg-green-50' : ''}`}
                  >
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="text-sm font-medium text-gray-900">
                          {statement.card_issuer || 'Unknown'}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">{statement.card_number?.value || 'N/A'}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">{statement.statement_date?.value ? formatDate(statement.statement_date.value) : 'N/A'}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">{statement.total_amount_due?.value || 'N/A'}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-500">
                        {statement.created_at ? formatTimestamp(statement.created_at) : 'Unknown'}
                        {isRecentStatement(statement) && (
                          <span className="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                            New
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <Link 
                        href={`/statement/${statement.job_id}`}
                        className="text-blue-600 hover:text-blue-900"
                      >
                        View Details
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          
            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex items-center justify-between mt-4">
                <div className="text-sm text-gray-700">
                  Showing <span className="font-medium">{(currentPage - 1) * itemsPerPage + 1}</span> to{' '}
                  <span className="font-medium">
                    {Math.min(currentPage * itemsPerPage, filteredStatements.length)}
                  </span>{' '}
                  of <span className="font-medium">{filteredStatements.length}</span> results
                </div>
                <div className="flex space-x-2">
                  <button
                    onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
                    disabled={currentPage === 1}
                    className="inline-flex items-center px-3 py-1 border border-white/40 rounded-md bg-white/70 backdrop-blur supports-[backdrop-filter]:backdrop-blur-md text-gray-800 hover:bg-white/80 disabled:opacity-50"
                  >
                    <ChevronLeft className="mr-1 h-4 w-4" />
                    Previous
                  </button>
                  <button
                    onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))}
                    disabled={currentPage === totalPages}
                    className="inline-flex items-center px-3 py-1 border border-white/40 rounded-md bg-white/70 backdrop-blur supports-[backdrop-filter]:backdrop-blur-md text-gray-800 hover:bg-white/80 disabled:opacity-50"
                  >
                    Next
                    <ChevronRight className="ml-1 h-4 w-4" />
                  </button>
                </div>
              </div>
            )}
          </>
        )}
      </main>
      <footer className="text-center py-6 text-gray-600 text-sm">
        <p>Built with Next.js • FastAPI • MongoDB</p>
        <p className="mt-2">Supports Kotak, HDFC, ICICI, Amex, and Capital One</p>
      </footer>
    </div>
  )
}
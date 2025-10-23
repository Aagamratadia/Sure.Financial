import axios from 'axios'
import type { ParseResult } from '@/types'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

/**
 * Save parsed statement result to database
 */
export async function saveResultToDatabase(result: ParseResult): Promise<{ success: boolean; message: string; result_id?: string }> {
  try {
    const response = await axios.post(
      `${API_BASE_URL}/api/v1/results/save`,
      result,
      {
        headers: {
          'Content-Type': 'application/json',
        },
      }
    )
    
    return {
      success: true,
      message: 'Result saved successfully',
      result_id: response.data.result_id
    }
  } catch (error: any) {
    console.error('Error saving result to database:', error)
    
    // For demo purposes, simulate successful save
    // This can be removed once the backend is fully implemented
    if (process.env.NODE_ENV === 'development') {
      return {
        success: true,
        message: 'Result saved successfully (simulated)',
        result_id: 'sim_' + Math.random().toString(36).substring(2, 15)
      }
    }
    
    return {
      success: false,
      message: error.response?.data?.detail || error.message || 'Failed to save result'
    }
  }
}

/**
 * Get saved result from database by ID
 */
export async function getResultFromDatabase(resultId: string): Promise<ParseResult | null> {
  try {
    const response = await axios.get(`${API_BASE_URL}/api/v1/results/${resultId}`)
    return response.data.raw_data
  } catch (error: any) {
    console.error('Error retrieving result from database:', error)
    return null
  }
}
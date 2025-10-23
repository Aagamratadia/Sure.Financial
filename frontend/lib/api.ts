import axios from 'axios'
import type { UploadResponse, JobStatusResponse, ParseResult, HealthResponse } from '@/types'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
})

/**
 * Upload a credit card statement PDF for parsing
 */
export async function uploadStatement(file: File): Promise<ParseResult> {
  const formData = new FormData()
  formData.append('file', file)

  try {
    const response = await axios.post<UploadResponse>(
      `${API_BASE_URL}/api/v1/parse/upload`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    )

    // If the response includes the result directly, return it
    if (response.data.result) {
      return response.data.result
    }

    // Otherwise, poll for the result
    const jobId = response.data.job_id
    return await pollJobStatus(jobId)
  } catch (error: any) {
    if (axios.isAxiosError(error)) {
      const message = error.response?.data?.detail || error.message
      throw new Error(`Upload failed: ${message}`)
    }
    throw error
  }
}

/**
 * Get the status of a parsing job
 */
export async function getJobStatus(jobId: string): Promise<JobStatusResponse> {
  try {
    const response = await api.get<JobStatusResponse>(`/parse/status/${jobId}`)
    return response.data
  } catch (error: any) {
    if (axios.isAxiosError(error)) {
      const message = error.response?.data?.detail || error.message
      throw new Error(`Failed to get job status: ${message}`)
    }
    throw error
  }
}

/**
 * Poll for job completion with exponential backoff
 */
async function pollJobStatus(
  jobId: string,
  maxAttempts: number = 30,
  initialDelay: number = 1000
): Promise<ParseResult> {
  let attempts = 0
  let delay = initialDelay

  while (attempts < maxAttempts) {
    try {
      const status = await getJobStatus(jobId)

      if (status.status === 'completed' && status.result) {
        return status.result
      }

      if (status.status === 'failed') {
        throw new Error(status.result?.error || 'Parsing failed')
      }

      // Wait before next poll
      await new Promise(resolve => setTimeout(resolve, delay))
      
      // Exponential backoff (but cap at 5 seconds)
      delay = Math.min(delay * 1.5, 5000)
      attempts++
    } catch (error) {
      if (attempts === maxAttempts - 1) {
        throw error
      }
      attempts++
      await new Promise(resolve => setTimeout(resolve, delay))
    }
  }

  throw new Error('Polling timeout: Job took too long to complete')
}

/**
 * Get the parsing result for a completed job
 */
export async function getJobResult(jobId: string): Promise<ParseResult> {
  try {
    const response = await api.get<ParseResult>(`/parse/results/${jobId}`)
    return response.data
  } catch (error: any) {
    if (axios.isAxiosError(error)) {
      const message = error.response?.data?.detail || error.message
      throw new Error(`Failed to get job result: ${message}`)
    }
    throw error
  }
}

/**
 * Upload multiple statements in batch
 */
export async function uploadBatchStatements(files: File[]): Promise<UploadResponse[]> {
  const formData = new FormData()
  files.forEach(file => {
    formData.append('files', file)
  })

  try {
    const response = await axios.post<UploadResponse[]>(
      `${API_BASE_URL}/api/v1/parse/batch`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    )
    return response.data
  } catch (error: any) {
    if (axios.isAxiosError(error)) {
      const message = error.response?.data?.detail || error.message
      throw new Error(`Batch upload failed: ${message}`)
    }
    throw error
  }
}

/**
 * Check API health status
 */
export async function checkHealth(): Promise<HealthResponse> {
  try {
    const response = await api.get<HealthResponse>('/health')
    return response.data
  } catch (error: any) {
    if (axios.isAxiosError(error)) {
      const message = error.response?.data?.detail || error.message
      throw new Error(`Health check failed: ${message}`)
    }
    throw error
  }
}

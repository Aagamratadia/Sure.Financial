// API utility functions for the frontend
import { ParseResult, JobStatusResponse } from '@/types';

// API base URL
// Ensure the base URL ALWAYS ends with '/api/v1' to match backend `settings.API_PREFIX`
function ensureApiV1(url: string): string {
  const base = url.replace(/\/$/, '');
  // If it already ends with /api/v1 (or any /api/v{number}), keep as-is
  if (/\/api\/v\d+$/.test(base)) return base;
  return `${base}/api/v1`;
}

const RAW_BASE_URL = (
  process.env.NEXT_PUBLIC_API_BASE_URL ||
  (typeof window !== 'undefined' && window.location.hostname !== 'localhost'
    ? 'https://rag-cloud-test-production.up.railway.app'
    : 'http://localhost:8000')
);

export const API_BASE_URL = ensureApiV1(RAW_BASE_URL);

/**
 * Upload a statement file for processing
 * @param file The statement file to upload
 * @returns Promise with the upload response
 */
export async function uploadStatement(file: File): Promise<ParseResult> {
  return uploadFile(file);
}

/**
 * Upload a file to the API for processing
 * @param file The file to upload
 * @returns Promise with the upload response
 */
export async function uploadFile(file: File): Promise<ParseResult> {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE_URL}/parse/upload`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    throw new Error(`Upload failed: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Check the status of a job
 * @param jobId The ID of the job to check
 * @returns Promise with the job status response
 */
export async function checkJobStatus(jobId: string): Promise<JobStatusResponse> {
  const response = await fetch(`${API_BASE_URL}/parse/status/${jobId}`);
  
  if (!response.ok) {
    throw new Error(`Status check failed: ${response.statusText}`);
  }
  
  return response.json();
}
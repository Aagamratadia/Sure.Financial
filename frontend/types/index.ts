// Type definitions for API responses

export interface DateField {
  value: string | null
  confidence: number
  raw_text?: string
}

export interface AmountField {
  value: string | null
  confidence: number
  raw_text?: string
  currency?: string
}

export interface DateRangeField {
  start_date: string | null
  end_date: string | null
  confidence: number
  raw_text?: string
}

export interface ConfidenceScores {
  overall: number
  card_number?: number
  statement_date?: number
  billing_period?: number
  total_amount_due?: number
  payment_due_date?: number
}

export interface ParseResult {
  job_id: string
  status: 'completed' | 'failed' | 'processing'
  card_issuer?: string
  parser_used?: string
  card_number?: {
    value: string | null
    confidence: number
    raw_text?: string
  }
  statement_date?: DateField
  billing_period?: DateRangeField
  total_amount_due?: AmountField
  payment_due_date?: DateField
  confidence_scores?: ConfidenceScores
  error?: string
  processing_time?: number
}

export interface UploadResponse {
  job_id: string
  status: string
  result?: ParseResult
}

export interface JobStatusResponse {
  job_id: string
  status: 'processing' | 'completed' | 'failed'
  created_at: string
  updated_at: string
  result?: ParseResult
}

export interface HealthResponse {
  status: string
  database: string
  timestamp: string
}

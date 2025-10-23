import axios from 'axios'
import type { ParseResult } from '@/types'

const API_BASE_URL = (process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1').replace(/\/$/, '')

// Fallback mock data in case MongoDB connection fails
const MOCK_STATEMENTS: ParseResult[] = [
  {
    job_id: 'job_1',
    status: 'completed',
    card_issuer: 'Axis Bank',
    card_number: { value: '9410', confidence: 95 },
    statement_date: { value: '2024-08-16', confidence: 90 },
    total_amount_due: { value: 'INR 40,491.00', confidence: 92 },
    payment_due_date: { value: '2024-10-05', confidence: 90 },
    confidence_scores: { overall: 94 },
    created_at: new Date().toISOString()
  },
  {
    job_id: 'job_2',
    status: 'completed',
    card_issuer: 'HDFC Bank',
    card_number: { value: '4567', confidence: 98 },
    statement_date: { value: '2024-07-20', confidence: 95 },
    total_amount_due: { value: 'INR 12,350.00', confidence: 96 },
    payment_due_date: { value: '2024-08-15', confidence: 97 },
    confidence_scores: { overall: 97 },
    created_at: new Date(Date.now() - 86400000).toISOString() // 1 day ago
  },
  {
    job_id: 'job_3',
    status: 'completed',
    card_issuer: 'ICICI Bank',
    card_number: { value: '7890', confidence: 92 },
    statement_date: { value: '2024-09-01', confidence: 93 },
    total_amount_due: { value: 'INR 8,745.50', confidence: 91 },
    payment_due_date: { value: '2024-09-25', confidence: 94 },
    confidence_scores: { overall: 92 },
    created_at: new Date(Date.now() - 172800000).toISOString() // 2 days ago
  },
  {
    job_id: 'job_4',
    status: 'completed',
    card_issuer: 'SBI Card',
    card_number: { value: '1234', confidence: 96 },
    statement_date: { value: '2024-08-05', confidence: 97 },
    total_amount_due: { value: 'INR 22,680.75', confidence: 95 },
    payment_due_date: { value: '2024-08-28', confidence: 98 },
    confidence_scores: { overall: 96 },
    created_at: new Date(Date.now() - 259200000).toISOString() // 3 days ago
  },
  {
    job_id: 'job_5',
    status: 'completed',
    card_issuer: 'Axis Bank',
    card_number: { value: '5678', confidence: 94 },
    statement_date: { value: '2024-07-10', confidence: 91 },
    total_amount_due: { value: 'INR 15,320.25', confidence: 93 },
    payment_due_date: { value: '2024-08-05', confidence: 92 },
    confidence_scores: { overall: 93 },
    created_at: new Date(Date.now() - 345600000).toISOString() // 4 days ago
  }
];

// Cache mechanism to reduce API calls
let statementsCache = {
  data: null as ParseResult[] | null,
  timestamp: 0
};
const CACHE_TTL = 10000; // 10 seconds

// Map a MongoDB result doc to ParseResult expected by UI
function mapDbToParseResult(doc: any): ParseResult {
  // 1) If backend saved raw ParseResult as raw_data, prefer that
  const rd = doc?.raw_data || {};
  if (Object.keys(rd).length > 0) {
    return {
      job_id: String(doc?._id || rd.job_id || doc?.job_id || ''),
      status: rd.status || 'completed',
      card_issuer: rd.card_issuer || 'Unknown',
      card_number: rd.card_number,
      statement_date: rd.statement_date,
      payment_due_date: rd.payment_due_date,
      total_amount_due: rd.total_amount_due,
      confidence_scores: rd.confidence_scores,
      created_at: rd.created_at || doc?.created_at || new Date().toISOString(),
    } as ParseResult;
  }

  // 2) Handle documents from repository 'results' collection (nested shape)
  const d = doc?.data || {};
  const cs = doc?.confidence_scores || {};

  const cardNumberVal = d.card_number
    ? (typeof d.card_number === 'string' ? d.card_number : String(d.card_number))
    : doc?.card_number;

  const statementDateVal = d.statement_period?.end_date || d.statement_date?.formatted || d.statement_date;
  const paymentDueVal = d.payment_due_date?.formatted || d.payment_due_date?.raw || doc?.due_date;
  const totalAmountVal = d.total_amount_due?.raw || d.total_amount_due?.amount || doc?.total_amount_due;

  const overall = cs.overall ?? cs.average ?? doc?.overall_confidence;

  return {
    job_id: String(doc?._id || doc?.job_id || ''),
    status: doc?.status || 'completed',
    card_issuer: d.card_issuer || doc?.card_issuer || doc?.issuer || 'Unknown',
    card_number: cardNumberVal ? { value: String(cardNumberVal) } : undefined,
    statement_date: statementDateVal ? { value: String(statementDateVal) } : undefined,
    payment_due_date: paymentDueVal ? { value: String(paymentDueVal) } : undefined,
    total_amount_due: totalAmountVal ? { value: String(totalAmountVal) } : undefined,
    confidence_scores: overall !== undefined ? { overall: Number(overall) } : undefined,
    created_at: doc?.created_at || new Date().toISOString(),
  } as ParseResult;
}

/**
 * Get all saved statements from MongoDB
 */
export async function getAllSavedStatements(forceRefresh = false): Promise<ParseResult[]> {
  // Check if we have cached data that's still valid
  const now = Date.now();
  if (!forceRefresh && statementsCache.data && now - statementsCache.timestamp < CACHE_TTL) {
    return statementsCache.data;
  }

  try {
    const response = await axios.get(`${API_BASE_URL}/results`, { params: { limit: 100 } });
    const docs = Array.isArray(response.data) ? response.data : [];
    const mapped: ParseResult[] = docs.map(mapDbToParseResult);
    statementsCache.data = mapped;
    statementsCache.timestamp = now;
    return mapped;
  } catch (error) {
    console.error('Error fetching results from API, falling back to mock data:', error);
    statementsCache.data = MOCK_STATEMENTS;
    statementsCache.timestamp = now;
    return MOCK_STATEMENTS;
  }
}

/**
 * Get saved statement by ID from MongoDB
 */
export async function getSavedStatementById(statementId: string): Promise<ParseResult | null> {
  try {
    // Check cache first
    const cachedStatement = statementsCache.data?.find(s => s.job_id === statementId);
    if (cachedStatement) {
      return cachedStatement;
    }
    
    // Make API call to fetch specific statement
    const response = await axios.get(`${API_BASE_URL}/results/${statementId}`);
    const mapped = mapDbToParseResult(response.data);
    // Optionally add to cache
    addStatementToCache(mapped);
    return mapped;
  } catch (error: any) {
    console.error('Error retrieving statement:', error);
    
    // If API call fails, try to find in mock data
    const mockStatement = MOCK_STATEMENTS.find(s => s.job_id === statementId);
    return mockStatement || null;
  }
}

/**
 * Add a new statement to the cache (for real-time updates)
 */
export function addStatementToCache(statement: ParseResult): void {
  if (!statementsCache.data) {
    statementsCache.data = [statement];
  } else {
    // Check if statement already exists
    const existingIndex = statementsCache.data.findIndex(s => s.job_id === statement.job_id);
    if (existingIndex >= 0) {
      statementsCache.data[existingIndex] = statement;
    } else {
      statementsCache.data.unshift(statement);
    }
  }
  statementsCache.timestamp = Date.now();
}
/**
 * Clear the statements cache
 */
export function clearStatementsCache(): void {
  statementsCache.data = null;
  statementsCache.timestamp = 0;
}
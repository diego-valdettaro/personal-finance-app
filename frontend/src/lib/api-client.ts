// Base API configuration
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000"
const AUTH_STRATEGY = import.meta.env.VITE_AUTH_STRATEGY || "bearer"

// Generic API response wrapper
export interface ApiResponse<T = unknown> {
  data: T
  message?: string
  success: boolean
}

// Pagination metadata
export interface PaginationMeta {
  page: number
  pageSize: number
  total: number
  totalPages: number
}

// Generic paginated response
export interface PaginatedResponse<T> extends ApiResponse<T[]> {
  meta: PaginationMeta
}

// Error types
export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public code?: string
  ) {
    super(message)
    this.name = "ApiError"
  }
}

// HTTP client with retry logic and interceptors
class ApiClient {
  private baseURL: string
  private authStrategy: string
  private token: string | null = null

  constructor(baseURL: string, authStrategy: string) {
    this.baseURL = baseURL
    this.authStrategy = authStrategy
    this.loadToken()
  }

  private loadToken() {
    if (this.authStrategy === "bearer") {
      this.token = localStorage.getItem("access_token")
    }
  }

  setToken(token: string | null) {
    this.token = token
    if (token) {
      localStorage.setItem("access_token", token)
    } else {
      localStorage.removeItem("access_token")
    }
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`
    
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      ...(options.headers as Record<string, string>),
    }

    // Add authentication
    if (this.token && this.authStrategy === "bearer") {
      headers.Authorization = `Bearer ${this.token}`
    }

    const config: RequestInit = {
      ...options,
      headers,
    }

    try {
      const response = await fetch(url, config)
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new ApiError(
          errorData.message || `HTTP ${response.status}`,
          response.status,
          errorData.code
        )
      }

      const data = await response.json()
      return data
    } catch (error) {
      if (error instanceof ApiError) {
        throw error
      }
      
      // Network or other errors
      throw new ApiError(
        error instanceof Error ? error.message : "Network error",
        0
      )
    }
  }

  async get<T>(endpoint: string, params?: Record<string, unknown> | object): Promise<T> {
    const searchParams = new URLSearchParams()
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          searchParams.append(key, String(value))
        }
      })
    }
    
    const url = searchParams.toString() 
      ? `${endpoint}?${searchParams.toString()}`
      : endpoint

    return this.request<T>(url, { method: "GET" })
  }

  async post<T>(endpoint: string, data?: unknown): Promise<T> {
    return this.request<T>(endpoint, {
      method: "POST",
      body: data ? JSON.stringify(data) : undefined,
    })
  }

  async put<T>(endpoint: string, data?: unknown): Promise<T> {
    return this.request<T>(endpoint, {
      method: "PUT",
      body: data ? JSON.stringify(data) : undefined,
    })
  }

  async patch<T>(endpoint: string, data?: unknown): Promise<T> {
    return this.request<T>(endpoint, {
      method: "PATCH",
      body: data ? JSON.stringify(data) : undefined,
    })
  }

  async delete<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: "DELETE" })
  }
}

// Create singleton instance
export const apiClient = new ApiClient(API_BASE_URL, AUTH_STRATEGY)

// Backend discovery utilities
export async function discoverBackendSchema() {
  try {
    // Try to get OpenAPI spec first
    const spec = await apiClient.get("/openapi.json")
    return { type: "openapi", spec }
  } catch {
    try {
      // Try Swagger spec
      const spec = await apiClient.get("/swagger.json")
      return { type: "swagger", spec }
    } catch {
      // Fallback to discovery via sample requests
      return { type: "discovery", spec: await discoverViaSampling() }
    }
  }
}

async function discoverViaSampling() {
  const endpoints = [
    "/accounts",
    "/transactions", 
    "/budgets",
    "/reports",
    "/people",
    "/categories"
  ]

  const results: Record<string, unknown> = {}

  for (const endpoint of endpoints) {
    try {
      const data = await apiClient.get(endpoint, { limit: 1 })
      results[endpoint] = data
    } catch (error) {
      // Endpoint doesn't exist or requires auth
      console.warn(`Could not discover ${endpoint}:`, error)
    }
  }

  return results
}

// Generic type inference utilities
export function inferTypeFromValue(value: unknown): string {
  if (value === null || value === undefined) return "unknown"
  if (typeof value === "boolean") return "boolean"
  if (typeof value === "number") return "number"
  if (typeof value === "string") {
    // Try to detect date strings
    if (!isNaN(Date.parse(value))) return "date"
    // Try to detect email
    if (value.includes("@")) return "email"
    return "string"
  }
  if (Array.isArray(value)) return "array"
  if (typeof value === "object") return "object"
  return "unknown"
}

// Field mapping utilities
export function mapFieldName(backendField: string, mappings: Record<string, string> = {}): string {
  // Common field mappings
  const commonMappings: Record<string, string> = {
    amount_cents: "amount",
    posted_at: "date",
    created_at: "createdAt",
    updated_at: "updatedAt",
    user_id: "userId",
    account_id: "accountId",
    transaction_id: "transactionId",
    ...mappings
  }

  return commonMappings[backendField] || backendField
}

// Currency conversion utilities
export function convertCurrency(
  amount: number,
  fromCurrency: string,
  toCurrency: string,
  rates: Record<string, number>
): number {
  if (fromCurrency === toCurrency) return amount
  if (!rates[fromCurrency] || !rates[toCurrency]) return amount
  
  // Convert to USD first, then to target currency
  const usdAmount = amount / rates[fromCurrency]
  return usdAmount * rates[toCurrency]
}

// Export the client for use in adapters
export { ApiClient }

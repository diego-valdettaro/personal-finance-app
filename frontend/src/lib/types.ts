// Central type definitions for the finance app

// API Error type
export interface ApiError {
  status?: number
  message?: string
}

// Enums (matching backend)
export enum AccountType {
  ASSET = "asset",
  LIABILITY = "liability",
  INCOME = "income",
  EXPENSE = "expense"
}

export enum TxType {
  TRANSFER = "transfer",
  INCOME = "income",
  EXPENSE = "expense",
  FOREX = "forex"
}

export enum TxSource {
  MANUAL = "manual",
  IMPORT = "import",
  API = "api"
}

// Filter interfaces
export interface AccountFilters {
  page?: number
  pageSize?: number
  search?: string
  type?: AccountType
}

export interface TransactionFilters {
  page?: number
  pageSize?: number
  search?: string
  accountId?: number
  type?: TxType
  startDate?: string
  endDate?: string
}

export interface BudgetFilters {
  page?: number
  pageSize?: number
  search?: string
  year?: number
}

export interface ReportFilters {
  page?: number
  pageSize?: number
  search?: string
  startDate?: string
  endDate?: string
}

// Base backend types (closer to actual API)
export interface BackendTransaction {
  id: number
  date: string
  type: TxType
  description?: string
  source: TxSource
  amount_oc_primary: number
  currency_primary: string
  account_id_primary: number
  account_id_secondary: number
  active: boolean
  tx_amount_hc: number
  postings: BackendPosting[]
  splits: BackendSplit[]
}

export interface BackendPosting {
  id: number
  tx_id: number
  account_id: number
  amount_oc: number
  currency: string
  fx_rate?: number
  amount_hc: number
}

export interface BackendSplit {
  id: number
  tx_id: number
  person_id: number
  share_amount: number
  active: boolean
  deleted_at?: string
}

export interface BackendAccount {
  id: number
  name: string
  type: AccountType
  currency?: string
  bank_name?: string
  opening_balance?: number
  billing_day?: number
  due_day?: number
}

export interface BackendUser {
  id: number
  name: string
  email: string
  home_currency: string
}

export interface BackendPerson {
  id: number
  name: string
  is_me: boolean
}

export interface BackendBudget {
  id: number
  name: string
  year: number
  lines: BackendBudgetLine[]
}

export interface BackendBudgetLine {
  id: number
  header_id: number
  month: number
  account_id: number
  amount_oc: number
  currency: string
  amount_hc: number
  fx_rate?: number
  description?: string
}

// Frontend UI-optimized types
export interface Transaction {
  id: string
  amount: number
  date: string
  description: string
  accountName?: string
  category?: string
  currency: string
  type: TxType
  source: TxSource
  isActive: boolean
  homeCurrencyAmount: number
  postings: Posting[]
  splits: Split[]
}

export interface Posting {
  id: string
  accountId: string
  amount: number
  currency: string
  fxRate?: number
  homeCurrencyAmount: number
}

export interface Split {
  id: string
  personId: string
  shareAmount: number
  isActive: boolean
  deletedAt?: string
}

export interface Account {
  id: string
  name: string
  type: AccountType
  currency?: string
  bankName?: string
  openingBalance?: number
  billingDay?: number
  dueDay?: number
  balance?: number // Calculated field
}

export interface User {
  id: string
  name: string
  email: string
  homeCurrency: string
}

export interface Person {
  id: string
  name: string
  isMe: boolean
}

export interface Budget {
  id: string
  name: string
  year: number
  lines: BudgetLine[]
}

export interface BudgetLine {
  id: string
  month: number
  accountId: string
  amount: number
  currency: string
  homeCurrencyAmount: number
  fxRate?: number
  description?: string
}

// Report data interfaces
export interface CategoryData {
  name: string
  value: number
  percentage: number
  [key: string]: string | number
}

export interface MonthlyData {
  month: string
  income: number
  expenses: number
}

export interface AccountBalanceData {
  name: string
  balance: number
  currency: string
}

// Dashboard types
export interface DashboardSummary {
  netWorth: number
  monthlyIncome: number
  monthlyExpenses: number
  savingsRate: number
  accountBalances: Array<{ account: Account; balance: number }>
  recentTransactions: Transaction[]
}

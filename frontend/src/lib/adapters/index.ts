// Adapter layer - translates backend responses to UI-friendly shapes
// This layer decouples the UI from the backend contract

import { apiClient, PaginatedResponse } from "../api-client"
import { 
  BackendTransaction, 
  BackendAccount, 
  BackendUser, 
  BackendPerson, 
  BackendBudget,
  BackendPosting,
  BackendSplit,
  BackendBudgetLine,
  Transaction, 
  Account, 
  User, 
  Person, 
  Budget,
  Posting,
  Split,
  BudgetLine,
  AccountFilters,
  TransactionFilters,
  BudgetFilters,
  ReportFilters,
  DashboardSummary,
  AccountType,
  TxType,
  TxSource
} from "../types"

// Re-export types for convenience
export type { 
  Transaction, 
  Account, 
  User, 
  Person, 
  Budget,
  Posting,
  Split,
  BudgetLine,
  AccountFilters,
  TransactionFilters,
  BudgetFilters,
  ReportFilters,
  DashboardSummary
} from "../types"

// Adapter functions that map backend responses to UI types
export const accountAdapter = {
  // Transform backend account to frontend account
  fromBackend: (backend: BackendAccount): Account => ({
    id: backend.id.toString(),
    name: backend.name,
    type: backend.type,
    currency: backend.currency,
    bankName: backend.bank_name,
    openingBalance: backend.opening_balance,
    billingDay: backend.billing_day,
    dueDay: backend.due_day,
    // Note: balance is calculated separately and added by the service layer
  }),

  // Transform frontend account to backend account (for create/update)
  toBackend: (frontend: Partial<Account>): Partial<BackendAccount> => ({
    id: frontend.id ? parseInt(frontend.id) : undefined,
    name: frontend.name,
    type: frontend.type,
    currency: frontend.currency,
    bank_name: frontend.bankName,
    opening_balance: frontend.openingBalance,
    billing_day: frontend.billingDay,
    due_day: frontend.dueDay,
  }),
}

export const transactionAdapter = {
  // Transform backend transaction to frontend transaction
  fromBackend: (backend: BackendTransaction): Transaction => ({
    id: backend.id.toString(),
    amount: backend.amount_oc_primary,
    date: backend.date,
    description: backend.description || "",
    currency: backend.currency_primary,
    type: backend.type,
    source: backend.source,
    isActive: backend.active,
    homeCurrencyAmount: backend.tx_amount_hc,
    accountName: undefined, // Will be populated by service layer
    category: undefined, // Will be populated by service layer
    postings: backend.postings.map(postingAdapter.fromBackend),
    splits: backend.splits.map(splitAdapter.fromBackend),
  }),

  // Transform frontend transaction to backend transaction (for create/update)
  toBackend: (frontend: Partial<Transaction>): Partial<BackendTransaction> => ({
    id: frontend.id ? parseInt(frontend.id) : undefined,
    date: frontend.date,
    type: frontend.type,
    description: frontend.description,
    amount_oc_primary: frontend.amount,
    currency_primary: frontend.currency,
    // Note: account_id_primary and account_id_secondary need to be handled separately
  }),
}

export const postingAdapter = {
  fromBackend: (backend: BackendPosting): Posting => ({
    id: backend.id.toString(),
    accountId: backend.account_id.toString(),
    amount: backend.amount_oc,
    currency: backend.currency,
    fxRate: backend.fx_rate,
    homeCurrencyAmount: backend.amount_hc,
  }),

  toBackend: (frontend: Partial<Posting>): Partial<BackendPosting> => ({
    id: frontend.id ? parseInt(frontend.id) : undefined,
    account_id: frontend.accountId ? parseInt(frontend.accountId) : undefined,
    amount_oc: frontend.amount,
    currency: frontend.currency,
    fx_rate: frontend.fxRate,
    amount_hc: frontend.homeCurrencyAmount,
  }),
}

export const splitAdapter = {
  fromBackend: (backend: BackendSplit): Split => ({
    id: backend.id.toString(),
    personId: backend.person_id.toString(),
    shareAmount: backend.share_amount,
    isActive: backend.active,
    deletedAt: backend.deleted_at,
  }),

  toBackend: (frontend: Partial<Split>): Partial<BackendSplit> => ({
    id: frontend.id ? parseInt(frontend.id) : undefined,
    person_id: frontend.personId ? parseInt(frontend.personId) : undefined,
    share_amount: frontend.shareAmount,
    active: frontend.isActive,
    deleted_at: frontend.deletedAt,
  }),
}

export const userAdapter = {
  fromBackend: (backend: BackendUser): User => ({
    id: backend.id.toString(),
    name: backend.name,
    email: backend.email,
    homeCurrency: backend.home_currency,
  }),

  toBackend: (frontend: Partial<User>): Partial<BackendUser> => ({
    id: frontend.id ? parseInt(frontend.id) : undefined,
    name: frontend.name,
    email: frontend.email,
    home_currency: frontend.homeCurrency,
  }),
}

export const personAdapter = {
  fromBackend: (backend: BackendPerson): Person => ({
    id: backend.id.toString(),
    name: backend.name,
    isMe: backend.is_me,
  }),

  toBackend: (frontend: Partial<Person>): Partial<BackendPerson> => ({
    id: frontend.id ? parseInt(frontend.id) : undefined,
    name: frontend.name,
    is_me: frontend.isMe,
  }),
}

export const budgetAdapter = {
  fromBackend: (backend: BackendBudget): Budget => ({
    id: backend.id.toString(),
    name: backend.name,
    year: backend.year,
    lines: backend.lines.map(budgetLineAdapter.fromBackend),
  }),

  toBackend: (frontend: Partial<Budget>): Partial<BackendBudget> => ({
    id: frontend.id ? parseInt(frontend.id) : undefined,
    name: frontend.name,
    year: frontend.year,
    lines: frontend.lines?.map(budgetLineAdapter.toBackend) as BackendBudgetLine[],
  }),
}

export const budgetLineAdapter = {
  fromBackend: (backend: BackendBudgetLine): BudgetLine => ({
    id: backend.id.toString(),
    month: backend.month,
    accountId: backend.account_id.toString(),
    amount: backend.amount_oc,
    currency: backend.currency,
    homeCurrencyAmount: backend.amount_hc,
    fxRate: backend.fx_rate,
    description: backend.description,
  }),

  toBackend: (frontend: Partial<BudgetLine>): Partial<BackendBudgetLine> => ({
    id: frontend.id ? parseInt(frontend.id) : undefined,
    month: frontend.month,
    account_id: frontend.accountId ? parseInt(frontend.accountId) : undefined,
    amount_oc: frontend.amount,
    currency: frontend.currency,
    amount_hc: frontend.homeCurrencyAmount,
    fx_rate: frontend.fxRate,
    description: frontend.description,
  }),
}

// Service layer - handles API calls and data transformation
export const adapters = {
  accounts: {
    list: async (filters: AccountFilters = {}): Promise<PaginatedResponse<Account>> => {
      const response = await apiClient.get<PaginatedResponse<BackendAccount>>("/accounts", filters as Record<string, unknown>)
      return {
        ...response,
        data: response.data.map(accountAdapter.fromBackend)
      }
    },

    get: async (id: string): Promise<Account> => {
      const response = await apiClient.get<BackendAccount>(`/accounts/${id}`)
      return accountAdapter.fromBackend(response)
    },

    create: async (account: Partial<Account>): Promise<Account> => {
      const backendData = accountAdapter.toBackend(account)
      const response = await apiClient.post<BackendAccount>("/accounts", backendData)
      return accountAdapter.fromBackend(response)
    },

    update: async (id: string, account: Partial<Account>): Promise<Account> => {
      const backendData = accountAdapter.toBackend(account)
      const response = await apiClient.put<BackendAccount>(`/accounts/${id}`, backendData)
      return accountAdapter.fromBackend(response)
    },

    delete: async (id: string): Promise<void> => {
      await apiClient.delete(`/accounts/${id}`)
    },
  },

  transactions: {
    list: async (filters: TransactionFilters = {}): Promise<PaginatedResponse<Transaction>> => {
      const response = await apiClient.get<PaginatedResponse<BackendTransaction>>("/transactions", filters as Record<string, unknown>)
      return {
        ...response,
        data: response.data.map(transactionAdapter.fromBackend)
      }
    },

    get: async (id: string): Promise<Transaction> => {
      const response = await apiClient.get<BackendTransaction>(`/transactions/${id}`)
      return transactionAdapter.fromBackend(response)
    },

    create: async (transaction: Partial<Transaction>): Promise<Transaction> => {
      const backendData = transactionAdapter.toBackend(transaction)
      const response = await apiClient.post<BackendTransaction>("/transactions", backendData)
      return transactionAdapter.fromBackend(response)
    },

    update: async (id: string, transaction: Partial<Transaction>): Promise<Transaction> => {
      const backendData = transactionAdapter.toBackend(transaction)
      const response = await apiClient.put<BackendTransaction>(`/transactions/${id}`, backendData)
      return transactionAdapter.fromBackend(response)
    },

    delete: async (id: string): Promise<void> => {
      await apiClient.delete(`/transactions/${id}`)
    },
  },

  budgets: {
    list: async (filters: BudgetFilters = {}): Promise<PaginatedResponse<Budget>> => {
      const response = await apiClient.get<PaginatedResponse<BackendBudget>>("/budgets", filters as Record<string, unknown>)
      return {
        ...response,
        data: response.data.map(budgetAdapter.fromBackend)
      }
    },

    get: async (id: string): Promise<Budget> => {
      const response = await apiClient.get<BackendBudget>(`/budgets/${id}`)
      return budgetAdapter.fromBackend(response)
    },

    create: async (budget: Partial<Budget>): Promise<Budget> => {
      const backendData = budgetAdapter.toBackend(budget)
      const response = await apiClient.post<BackendBudget>("/budgets", backendData)
      return budgetAdapter.fromBackend(response)
    },

    update: async (id: string, budget: Partial<Budget>): Promise<Budget> => {
      const backendData = budgetAdapter.toBackend(budget)
      const response = await apiClient.put<BackendBudget>(`/budgets/${id}`, backendData)
      return budgetAdapter.fromBackend(response)
    },

    delete: async (id: string): Promise<void> => {
      await apiClient.delete(`/budgets/${id}`)
    },
  },

  people: {
    list: async (): Promise<Person[]> => {
      const response = await apiClient.get<BackendPerson[]>("/people")
      return response.map(personAdapter.fromBackend)
    },

    get: async (id: string): Promise<Person> => {
      const response = await apiClient.get<BackendPerson>(`/people/${id}`)
      return personAdapter.fromBackend(response)
    },

    create: async (person: Partial<Person>): Promise<Person> => {
      const backendData = personAdapter.toBackend(person)
      const response = await apiClient.post<BackendPerson>("/people", backendData)
      return personAdapter.fromBackend(response)
    },

    update: async (id: string, person: Partial<Person>): Promise<Person> => {
      const backendData = personAdapter.toBackend(person)
      const response = await apiClient.put<BackendPerson>(`/people/${id}`, backendData)
      return personAdapter.fromBackend(response)
    },

    delete: async (id: string): Promise<void> => {
      await apiClient.delete(`/people/${id}`)
    },
  },

  users: {
    get: async (): Promise<User> => {
      const response = await apiClient.get<BackendUser>("/users/me")
      return userAdapter.fromBackend(response)
    },

    update: async (user: Partial<User>): Promise<User> => {
      const backendData = userAdapter.toBackend(user)
      const response = await apiClient.put<BackendUser>("/users/me", backendData)
      return userAdapter.fromBackend(response)
    },
  },

  reports: {
    budgetProgress: async (filters: ReportFilters = {}): Promise<unknown> => {
      return await apiClient.get("/reports/budget-progress", filters as Record<string, unknown>)
    },

    balances: async (filters: ReportFilters = {}): Promise<unknown> => {
      return await apiClient.get("/reports/balances", filters as Record<string, unknown>)
    },

    debts: async (filters: ReportFilters = {}): Promise<unknown> => {
      return await apiClient.get("/reports/debts", filters as Record<string, unknown>)
    },
  },

  dashboard: {
    getSummary: async (): Promise<DashboardSummary> => {
      // For now, return mock data since the backend requires authentication
      // TODO: Implement proper authentication flow
      const mockAccounts: Account[] = [
        {
          id: "1",
          name: "Checking Account",
          type: AccountType.ASSET,
          currency: "USD",
          balance: 2500.00
        },
        {
          id: "2", 
          name: "Savings Account",
          type: AccountType.ASSET,
          currency: "USD",
          balance: 15000.00
        },
        {
          id: "3",
          name: "Credit Card",
          type: AccountType.LIABILITY,
          currency: "USD", 
          balance: -1200.00
        }
      ]

      const mockTransactions: Transaction[] = [
        {
          id: "1",
          description: "Salary Deposit",
          amount: 5000.00,
          currency: "USD",
          date: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
          accountName: "Checking Account",
          category: "Income",
          type: TxType.INCOME,
          source: TxSource.MANUAL,
          isActive: true,
          homeCurrencyAmount: 5000.00,
          postings: [],
          splits: []
        },
        {
          id: "2",
          description: "Grocery Shopping",
          amount: -150.75,
          currency: "USD",
          date: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
          accountName: "Checking Account",
          category: "Food",
          type: TxType.EXPENSE,
          source: TxSource.MANUAL,
          isActive: true,
          homeCurrencyAmount: -150.75,
          postings: [],
          splits: []
        },
        {
          id: "3",
          description: "Rent Payment",
          amount: -1200.00,
          currency: "USD",
          date: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(),
          accountName: "Checking Account",
          category: "Housing",
          type: TxType.EXPENSE,
          source: TxSource.MANUAL,
          isActive: true,
          homeCurrencyAmount: -1200.00,
          postings: [],
          splits: []
        }
      ]

      const accounts = mockAccounts
      const transactions = mockTransactions
      
      // Calculate account balances
      const accountBalances = accounts.map(account => ({
        account,
        balance: account.balance || 0
      }))
      
      // Calculate metrics
      const netWorth = accountBalances.reduce((sum, { balance }) => sum + balance, 0)
      const monthlyIncome = transactions
        .filter(t => t.amount > 0)
        .reduce((sum, t) => sum + t.amount, 0)
      const monthlyExpenses = Math.abs(transactions
        .filter(t => t.amount < 0)
        .reduce((sum, t) => sum + t.amount, 0))
      const savingsRate = monthlyIncome > 0 ? ((monthlyIncome - monthlyExpenses) / monthlyIncome) * 100 : 0
      
      return {
        netWorth,
        monthlyIncome,
        monthlyExpenses,
        savingsRate,
        accountBalances,
        recentTransactions: transactions
      }
    },
  },
}
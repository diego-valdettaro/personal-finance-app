import { useState } from "react"
import { useQuery } from "@tanstack/react-query"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { adapters } from "@/lib/adapters"
import { queryKeys } from "@/lib/query-client"
import { formatCurrency } from "@/lib/utils"
import { 
  Download, 
  BarChart3, 
  PieChart, 
  TrendingUp,
  Filter
} from "lucide-react"
import { PieChart as RechartsPieChart, Pie, Cell, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from "recharts"
import { Transaction, Account, CategoryData, MonthlyData, AccountBalanceData } from "@/lib/types"


const reportTypes = [
  { id: "spending-by-category", name: "Spending by Category", icon: PieChart },
  { id: "monthly-trends", name: "Monthly Trends", icon: TrendingUp },
  { id: "account-balances", name: "Account Balances", icon: BarChart3 },
]

export function ReportsPage() {
  const [selectedReport, setSelectedReport] = useState("spending-by-category")
  const [dateRange, setDateRange] = useState("month")

  const { data: transactions } = useQuery({
    queryKey: queryKeys.transactions.list({ 
      startDate: getDateRangeStart(dateRange),
      endDate: new Date().toISOString(),
      pageSize: 1000 
    }),
    queryFn: () => adapters.transactions.list({ 
      startDate: getDateRangeStart(dateRange),
      endDate: new Date().toISOString(),
      pageSize: 1000 
    }),
  })

  const { data: accounts } = useQuery({
    queryKey: queryKeys.accounts.list({ pageSize: 100 }),
    queryFn: () => adapters.accounts.list({ pageSize: 100 }),
  })

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Reports</h1>
          <p className="text-muted-foreground">
            Analyze your financial data with detailed reports
          </p>
        </div>
        <Button>
          <Download className="h-4 w-4 mr-2" />
          Export Report
        </Button>
      </div>

      {/* Report controls */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Filter className="h-5 w-5" />
            Report Settings
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2">
            <div className="space-y-2">
              <label className="text-sm font-medium">Report Type</label>
              <Select value={selectedReport} onValueChange={setSelectedReport}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {reportTypes.map((report) => (
                    <SelectItem key={report.id} value={report.id}>
                      <div className="flex items-center gap-2">
                        <report.icon className="h-4 w-4" />
                        {report.name}
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Date Range</label>
              <Select value={dateRange} onValueChange={setDateRange}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="week">Last 7 days</SelectItem>
                  <SelectItem value="month">Last 30 days</SelectItem>
                  <SelectItem value="quarter">Last 3 months</SelectItem>
                  <SelectItem value="year">Last 12 months</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Report content */}
      <div className="grid gap-6">
        {selectedReport === "spending-by-category" && (
          <SpendingByCategoryReport data={generateSpendingByCategoryData(transactions?.data || [])} />
        )}
        {selectedReport === "monthly-trends" && (
          <MonthlyTrendsReport data={generateMonthlyTrendsData(transactions?.data || [])} />
        )}
        {selectedReport === "account-balances" && (
          <AccountBalancesReport data={generateAccountBalancesData(accounts?.data || [])} />
        )}
      </div>
    </div>
  )
}

function SpendingByCategoryReport({ data }: { data: CategoryData[] }) {
  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D']

  return (
    <div className="grid gap-6 md:grid-cols-2">
      <Card>
        <CardHeader>
          <CardTitle>Spending by Category</CardTitle>
          <CardDescription>
            Breakdown of expenses by category
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <RechartsPieChart>
                <Pie
                  data={data}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  // eslint-disable-next-line @typescript-eslint/no-explicit-any
                  label={(props: any) => `${props.name} ${(props.percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {data.map((_: CategoryData, index: number) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(value: number) => formatCurrency(value)} />
              </RechartsPieChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Category Details</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {data.map((item: CategoryData, index: number) => (
              <div key={item.name} className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div 
                    className="w-4 h-4 rounded-full" 
                    style={{ backgroundColor: COLORS[index % COLORS.length] }}
                  />
                  <span className="font-medium">{item.name}</span>
                </div>
                <div className="text-right">
                  <p className="font-medium">{formatCurrency(item.value)}</p>
                  <p className="text-sm text-muted-foreground">
                    {item.percentage.toFixed(1)}%
                  </p>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

function MonthlyTrendsReport({ data }: { data: MonthlyData[] }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Monthly Trends</CardTitle>
        <CardDescription>
          Income vs expenses over time
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip formatter={(value: number) => formatCurrency(value)} />
              <Legend />
              <Bar dataKey="income" fill="#00C49F" name="Income" />
              <Bar dataKey="expenses" fill="#FF8042" name="Expenses" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  )
}

function AccountBalancesReport({ data }: { data: AccountBalanceData[] }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Account Balances</CardTitle>
        <CardDescription>
          Current balances across all accounts
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data} layout="horizontal">
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" />
              <YAxis dataKey="name" type="category" width={100} />
              <Tooltip formatter={(value: number) => formatCurrency(value)} />
              <Bar dataKey="balance" fill="#8884d8" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  )
}

// Helper functions
function getDateRangeStart(range: string): string {
  const now = new Date()
  switch (range) {
    case "week":
      return new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000).toISOString()
    case "month":
      return new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000).toISOString()
    case "quarter":
      return new Date(now.getTime() - 90 * 24 * 60 * 60 * 1000).toISOString()
    case "year":
      return new Date(now.getTime() - 365 * 24 * 60 * 60 * 1000).toISOString()
    default:
      return new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000).toISOString()
  }
}


function generateSpendingByCategoryData(transactions: Transaction[]): CategoryData[] {
  const categoryTotals: Record<string, number> = {}
  
  transactions
    .filter(t => t.amount < 0) // Only expenses
    .forEach(transaction => {
      const category = transaction.category || "Uncategorized"
      categoryTotals[category] = (categoryTotals[category] || 0) + Math.abs(transaction.amount)
    })

  const total = Object.values(categoryTotals).reduce((sum, amount) => sum + amount, 0)
  
  return Object.entries(categoryTotals)
    .map(([name, value]) => ({
      name,
      value,
      percentage: (value / total) * 100
    }))
    .sort((a, b) => b.value - a.value)
}

function generateMonthlyTrendsData(transactions: Transaction[]): MonthlyData[] {
  const monthlyData: Record<string, { income: number; expenses: number }> = {}
  
  transactions.forEach(transaction => {
    const month = new Date(transaction.date).toLocaleDateString('en-US', { month: 'short', year: 'numeric' })
    if (!monthlyData[month]) {
      monthlyData[month] = { income: 0, expenses: 0 }
    }
    
    if (transaction.amount > 0) {
      monthlyData[month].income += transaction.amount
    } else {
      monthlyData[month].expenses += Math.abs(transaction.amount)
    }
  })

  return Object.entries(monthlyData)
    .map(([month, data]) => ({ month, ...data }))
    .sort((a, b) => new Date(a.month).getTime() - new Date(b.month).getTime())
}

function generateAccountBalancesData(accounts: Account[]): AccountBalanceData[] {
  return accounts.map(account => ({
    name: account.name,
    balance: account.balance || 0,
    currency: account.currency || 'EUR'
  }))
}

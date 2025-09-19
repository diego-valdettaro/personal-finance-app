import { useState } from "react"
import { useQuery } from "@tanstack/react-query"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { adapters, BudgetFilters, Budget } from "@/lib/adapters"
import { queryKeys } from "@/lib/query-client"
import { formatCurrency, calculatePercentage } from "@/lib/utils"
import { 
  Plus, 
  Edit, 
  Trash2, 
  TrendingUp,
  TrendingDown,
  Target,
  AlertCircle
} from "lucide-react"

export function BudgetsPage() {
  const [filters, setFilters] = useState<BudgetFilters>({
    year: new Date().getFullYear(),
  })
  const [selectedMonth, setSelectedMonth] = useState<number>(new Date().getMonth() + 1)

  const { data: budgets, isLoading, error } = useQuery({
    queryKey: queryKeys.budgets.list(filters),
    queryFn: () => adapters.budgets.list(filters),
  })

  const handleFilterChange = (key: keyof BudgetFilters, value: BudgetFilters[keyof BudgetFilters]) => {
    setFilters(prev => ({ ...prev, [key]: value }))
  }

  if (isLoading) {
    return <BudgetsSkeleton />
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <h3 className="text-lg font-semibold">Failed to load budgets</h3>
          <p className="text-muted-foreground">Please try again later</p>
        </div>
      </div>
    )
  }

  const totalPlanned = budgets?.data.reduce((sum, budget) => 
    sum + budget.lines.reduce((lineSum, line) => lineSum + line.amount, 0), 0) || 0
  const totalActual = budgets?.data.reduce((sum, budget) => 
    sum + budget.lines.reduce((lineSum, line) => lineSum + line.homeCurrencyAmount, 0), 0) || 0
  const totalVariance = totalActual - totalPlanned

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Budgets</h1>
          <p className="text-muted-foreground">
            Track your spending against planned budgets
          </p>
        </div>
        <Button>
          <Plus className="h-4 w-4 mr-2" />
          Add Budget
        </Button>
      </div>

      {/* Period selector */}
      <Card>
        <CardHeader>
          <CardTitle>Budget Period</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Year</label>
              <Select 
                value={filters.year?.toString()} 
                onValueChange={(value) => handleFilterChange("year", parseInt(value))}
              >
                <SelectTrigger className="w-32">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {Array.from({ length: 5 }, (_, i) => {
                    const year = new Date().getFullYear() - 2 + i
                    return (
                      <SelectItem key={year} value={year.toString()}>
                        {year}
                      </SelectItem>
                    )
                  })}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Month</label>
              <Select 
                value={selectedMonth.toString()} 
                onValueChange={(value) => setSelectedMonth(parseInt(value))}
              >
                <SelectTrigger className="w-40">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="0">All months</SelectItem>
                  {Array.from({ length: 12 }, (_, i) => {
                    const month = i + 1
                    const date = new Date(2024, i, 1)
                    return (
                      <SelectItem key={month} value={month.toString()}>
                        {date.toLocaleString('default', { month: 'long' })}
                      </SelectItem>
                    )
                  })}
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Summary cards */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Planned</CardTitle>
            <Target className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {formatCurrency(totalPlanned)}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Actual</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {formatCurrency(totalActual)}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Variance</CardTitle>
            {totalVariance >= 0 ? (
              <TrendingUp className="h-4 w-4 text-positive" />
            ) : (
              <TrendingDown className="h-4 w-4 text-negative" />
            )}
          </CardHeader>
          <CardContent>
            <div className={`text-2xl font-bold ${
              totalVariance >= 0 ? "text-positive" : "text-negative"
            }`}>
              {totalVariance >= 0 ? "+" : ""}{formatCurrency(totalVariance)}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Budgets list */}
      <Card>
        <CardHeader>
          <CardTitle>Budget Categories</CardTitle>
          <CardDescription>
            {budgets?.data.length || 0} budget categories for {filters.year}
            {selectedMonth > 0 && ` - ${new Date(2024, selectedMonth - 1, 1).toLocaleString('default', { month: 'long' })}`}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {budgets?.data.map((budget) => (
              <BudgetRow key={budget.id} budget={budget} />
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

function BudgetRow({ budget }: { budget: Budget }) {
  const plannedAmount = budget.lines.reduce((sum, line) => sum + line.amount, 0)
  const actualAmount = budget.lines.reduce((sum, line) => sum + line.homeCurrencyAmount, 0)
  const variance = actualAmount - plannedAmount
  const variancePercentage = plannedAmount > 0 
    ? calculatePercentage(Math.abs(variance), plannedAmount)
    : 0
  const isOverBudget = variance > 0

  return (
    <div className="flex items-center justify-between p-4 rounded-lg border hover:bg-accent/50 transition-colors">
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-3">
          <h3 className="font-medium">{budget.name}</h3>
          {isOverBudget && (
            <AlertCircle className="h-4 w-4 text-negative" />
          )}
        </div>
        <p className="text-sm text-muted-foreground">{budget.year}</p>
      </div>

      <div className="flex items-center gap-6">
        {/* Progress bar */}
        <div className="w-32 space-y-1">
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Progress</span>
            <span className="font-medium">{variancePercentage.toFixed(0)}%</span>
          </div>
          <div className="h-2 bg-muted rounded-full overflow-hidden">
            <div 
              className={`h-full transition-all duration-300 ${
                isOverBudget ? "bg-negative" : "bg-positive"
              }`}
              style={{ 
                width: `${Math.min(calculatePercentage(actualAmount, plannedAmount), 100)}%` 
              }}
            />
          </div>
        </div>

        {/* Amounts */}
        <div className="text-right space-y-1">
          <div className="flex items-center gap-4">
            <div>
              <p className="text-sm text-muted-foreground">Planned</p>
              <p className="font-medium">{formatCurrency(plannedAmount)}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Actual</p>
              <p className="font-medium">{formatCurrency(actualAmount)}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Variance</p>
                  <p className={`font-medium ${
                    variance >= 0 ? "text-positive" : "text-negative"
                  }`}>
                    {variance >= 0 ? "+" : ""}{formatCurrency(variance)}
                  </p>
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="flex gap-1">
          <Button variant="ghost" size="icon" className="h-8 w-8">
            <Edit className="h-4 w-4" />
          </Button>
          <Button variant="ghost" size="icon" className="h-8 w-8">
            <Trash2 className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </div>
  )
}

function BudgetsSkeleton() {
  return (
    <div className="space-y-6">
      {/* Header skeleton */}
      <div className="flex items-center justify-between">
        <div className="space-y-2">
          <div className="h-8 w-32 bg-muted rounded animate-pulse" />
          <div className="h-4 w-64 bg-muted rounded animate-pulse" />
        </div>
        <div className="h-10 w-32 bg-muted rounded animate-pulse" />
      </div>

      {/* Summary cards skeleton */}
      <div className="grid gap-4 md:grid-cols-3">
        {Array.from({ length: 3 }).map((_, i) => (
          <Card key={i}>
            <CardHeader className="space-y-0 pb-2">
              <div className="h-4 w-24 bg-muted rounded animate-pulse" />
            </CardHeader>
            <CardContent>
              <div className="h-8 w-32 bg-muted rounded animate-pulse" />
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Budgets list skeleton */}
      <Card>
        <CardHeader>
          <div className="h-6 w-32 bg-muted rounded animate-pulse" />
          <div className="h-4 w-48 bg-muted rounded animate-pulse" />
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {Array.from({ length: 5 }).map((_, i) => (
              <div key={i} className="flex items-center justify-between p-4 rounded-lg border">
                <div className="flex-1 space-y-2">
                  <div className="h-4 w-32 bg-muted rounded animate-pulse" />
                  <div className="h-3 w-24 bg-muted rounded animate-pulse" />
                </div>
                <div className="flex items-center gap-6">
                  <div className="w-32 space-y-1">
                    <div className="h-3 w-16 bg-muted rounded animate-pulse" />
                    <div className="h-2 w-full bg-muted rounded animate-pulse" />
                  </div>
                  <div className="space-y-1">
                    <div className="h-4 w-20 bg-muted rounded animate-pulse" />
                    <div className="h-4 w-20 bg-muted rounded animate-pulse" />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

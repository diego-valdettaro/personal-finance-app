import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { useAuth } from "@/hooks/useAuth"
import { 
  ArrowRight, 
  CheckCircle, 
  DollarSign, 
  BarChart3, 
  Shield, 
  Smartphone,
  TrendingUp,
  PieChart,
  CreditCard,
} from "lucide-react"

export function LandingPage() {
  const [isLogin, setIsLogin] = useState(true)

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Navigation */}
      <nav className="sticky top-0 z-50 border-b border-slate-700/50 bg-slate-900/50 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-gradient-to-r from-green-400 to-green-600 rounded-lg flex items-center justify-center">
                <DollarSign className="w-5 h-5 text-white" />
              </div>
              <span className="text-xl font-bold text-white">FinanceApp</span>
            </div>
            <div className="flex items-center space-x-4">
              <Button 
                variant="ghost" 
                className="text-slate-300 hover:text-white"
                onClick={() => setIsLogin(true)}
              >
                Sign In
              </Button>
              <Button 
                className="bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700"
                onClick={() => setIsLogin(false)}
              >
                Get Started
              </Button>
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          {/* Left side - Hero content */}
          <div className="space-y-8">
            <div className="space-y-4">
              <h1 className="text-4xl lg:text-6xl font-bold text-white leading-tight">
                Take Control of Your
                <span className="bg-gradient-to-r from-green-400 to-green-600 bg-clip-text text-transparent">
                  {" "}Finances
                </span>
              </h1>
              <p className="text-xl text-slate-300 leading-relaxed">
                A modern, intuitive platform to manage your money, track expenses, 
                and achieve your financial goals with confidence.
              </p>
            </div>

            {/* Features grid */}
            <div className="grid grid-cols-2 gap-4">
              <div className="flex items-center space-x-3">
                <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0" />
                <span className="text-slate-300">Real-time tracking</span>
              </div>
              <div className="flex items-center space-x-3">
                <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0" />
                <span className="text-slate-300">Smart budgeting</span>
              </div>
              <div className="flex items-center space-x-3">
                <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0" />
                <span className="text-slate-300">Secure & private</span>
              </div>
              <div className="flex items-center space-x-3">
                <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0" />
                <span className="text-slate-300">Mobile friendly</span>
              </div>
            </div>

            {/* CTA buttons */}
            <div className="flex flex-col sm:flex-row gap-4">
              <Button 
                size="lg" 
                className="bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 text-lg px-8 py-3"
                onClick={() => setIsLogin(false)}
              >
                Start Free Trial
                <ArrowRight className="ml-2 w-5 h-5" />
              </Button>
              <Button 
                size="lg" 
                variant="outline" 
                className="border-slate-600 text-slate-300 hover:bg-slate-800 hover:text-white text-lg px-8 py-3"
                onClick={() => setIsLogin(true)}
              >
                Sign In
              </Button>
            </div>
          </div>

          {/* Right side - Auth form */}
          <div className="flex justify-center">
            <Card className="w-full max-w-md bg-slate-800/50 border-slate-700 backdrop-blur-sm">
              <CardHeader className="text-center">
                <CardTitle className="text-2xl text-white">
                  {isLogin ? "Welcome Back" : "Create Account"}
                </CardTitle>
                <CardDescription className="text-slate-400">
                  {isLogin 
                    ? "Sign in to your account to continue" 
                    : "Get started with your free account"
                  }
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <AuthForm isLogin={isLogin} />
                
                <div className="text-center">
                  <p className="text-slate-400">
                    {isLogin ? "Don't have an account?" : "Already have an account?"}
                  </p>
                  <Button
                    variant="link"
                    className="text-green-400 hover:text-green-300 p-0 h-auto"
                    onClick={() => setIsLogin(!isLogin)}
                  >
                    {isLogin ? "Sign up here" : "Sign in here"}
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Features section */}
        <div className="mt-24">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-white mb-4">
              Everything you need to manage your finances
            </h2>
            <p className="text-xl text-slate-400">
              Powerful features designed to help you take control of your money
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            <FeatureCard
              icon={<BarChart3 className="w-8 h-8" />}
              title="Smart Analytics"
              description="Get insights into your spending patterns with beautiful charts and reports."
            />
            <FeatureCard
              icon={<PieChart className="w-8 h-8" />}
              title="Budget Planning"
              description="Create and manage budgets that actually work for your lifestyle."
            />
            <FeatureCard
              icon={<CreditCard className="w-8 h-8" />}
              title="Transaction Tracking"
              description="Easily categorize and track all your income and expenses."
            />
            <FeatureCard
              icon={<Shield className="w-8 h-8" />}
              title="Bank-Level Security"
              description="Your data is protected with enterprise-grade security measures."
            />
            <FeatureCard
              icon={<Smartphone className="w-8 h-8" />}
              title="Mobile First"
              description="Access your finances anywhere with our responsive design."
            />
            <FeatureCard
              icon={<TrendingUp className="w-8 h-8" />}
              title="Goal Tracking"
              description="Set and track financial goals to achieve your dreams."
            />
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="border-t border-slate-700/50 bg-slate-900/50 backdrop-blur-sm mt-24">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center text-slate-400">
            <p>&copy; 2024 FinanceApp. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}

function AuthForm({ isLogin }: { isLogin: boolean }) {
  const { login, register, isLoading } = useAuth()
  const [formData, setFormData] = useState({
    email: "",
    password: "",
    confirmPassword: "",
    name: "",
    home_currency: "USD"
  })
  const [error, setError] = useState("")


  const handleSubmit = async (e?: React.MouseEvent) => {
    if (e) {
      e.preventDefault()
      e.stopPropagation()
    }
    
    // Only clear error if we're about to validate successfully
    // setError("") - moved this after validation
    
    // Client-side validation
    if (!formData.email || !formData.password) {
      setError("Please fill in all required fields")
      return
    }
    
    if (!isLogin && (!formData.name || formData.password !== formData.confirmPassword)) {
      if (!formData.name) {
        setError("Please enter your full name")
      } else {
        setError("Passwords do not match")
      }
      return
    }
    
    // Clear error only after validation passes
    setError("")
    
    try {
      if (isLogin) {
        await login(formData.email, formData.password)
      } else {
        await register(formData.name, formData.email, formData.password, formData.home_currency)
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "An error occurred"
      setError(errorMessage)
      // Prevent any further action that might cause page refresh
      return false
    }
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setFormData(prev => ({
      ...prev,
      [e.target.name]: e.target.value
    }))
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault()
      handleSubmit()
    }
  }

  return (
    <div 
      className="space-y-4" 
      onKeyDown={handleKeyDown}
      onSubmit={(e) => e.preventDefault()}
      onClick={(e) => e.stopPropagation()}
    >
      {error && (
        <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-3">
          <p className="text-red-400 text-sm">{error}</p>
        </div>
      )}
      
      {!isLogin && (
        <div className="space-y-2">
          <Label htmlFor="name" className="text-slate-300">Full Name</Label>
          <Input
            id="name"
            name="name"
            type="text"
            value={formData.name}
            onChange={handleChange}
            className="bg-slate-700/50 border-slate-600 text-white placeholder-slate-400"
            placeholder="Enter your full name"
          />
        </div>
      )}
      
      {!isLogin && (
        <div className="space-y-2">
          <Label htmlFor="home_currency" className="text-slate-300">Home Currency</Label>
          <select
            id="home_currency"
            name="home_currency"
            value={formData.home_currency}
            onChange={handleChange}
            className="w-full px-3 py-2 bg-slate-700/50 border border-slate-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-green-500"
          >
            <option value="USD">USD - US Dollar</option>
            <option value="EUR">EUR - Euro</option>
            <option value="GBP">GBP - British Pound</option>
            <option value="CAD">CAD - Canadian Dollar</option>
            <option value="AUD">AUD - Australian Dollar</option>
            <option value="JPY">JPY - Japanese Yen</option>
          </select>
        </div>
      )}
      
      <div className="space-y-2">
        <Label htmlFor="email" className="text-slate-300">Email</Label>
        <Input
          id="email"
          name="email"
          type="email"
          value={formData.email}
          onChange={handleChange}
          className="bg-slate-700/50 border-slate-600 text-white placeholder-slate-400"
          placeholder="Enter your email"
        />
      </div>
      
      <div className="space-y-2">
        <Label htmlFor="password" className="text-slate-300">Password</Label>
        <Input
          id="password"
          name="password"
          type="password"
          value={formData.password}
          onChange={handleChange}
          className="bg-slate-700/50 border-slate-600 text-white placeholder-slate-400"
          placeholder="Enter your password"
        />
      </div>
      
      {!isLogin && (
        <div className="space-y-2">
          <Label htmlFor="confirmPassword" className="text-slate-300">Confirm Password</Label>
          <Input
            id="confirmPassword"
            name="confirmPassword"
            type="password"
            value={formData.confirmPassword}
            onChange={handleChange}
            className="bg-slate-700/50 border-slate-600 text-white placeholder-slate-400"
            placeholder="Confirm your password"
          />
        </div>
      )}
      
      <Button 
        type="button" 
        className="w-full bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700"
        size="lg"
        disabled={isLoading}
        onClick={(e) => {
          e.preventDefault()
          e.stopPropagation()
          e.nativeEvent.stopImmediatePropagation()
          handleSubmit(e)
        }}
        onMouseDown={(e) => {
          e.preventDefault()
          e.stopPropagation()
        }}
        onMouseUp={(e) => {
          e.preventDefault()
          e.stopPropagation()
        }}
      >
        {isLoading ? (
          <div className="flex items-center">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
            {isLogin ? "Signing In..." : "Creating Account..."}
          </div>
        ) : (
          isLogin ? "Sign In" : "Create Account"
        )}
      </Button>
    </div>
  )
}

function FeatureCard({ 
  icon, 
  title, 
  description 
}: { 
  icon: React.ReactNode
  title: string
  description: string 
}) {
  return (
    <div className="bg-slate-800/30 border border-slate-700/50 rounded-xl p-6 hover:bg-slate-800/50 transition-colors">
      <div className="text-green-400 mb-4">
        {icon}
      </div>
      <h3 className="text-xl font-semibold text-white mb-2">{title}</h3>
      <p className="text-slate-400">{description}</p>
    </div>
  )
}

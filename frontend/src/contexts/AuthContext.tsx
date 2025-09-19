import { createContext, useState, useEffect, ReactNode } from "react"
import { apiClient } from "@/lib/api-client"

interface User {
  id: number
  name: string
  email: string
  home_currency: string
}

interface AuthContextType {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (email: string, password: string) => Promise<void>
  register: (name: string, email: string, password: string, home_currency: string) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // Check if user is logged in on app start
    const savedUser = localStorage.getItem("user")
    const savedToken = localStorage.getItem("access_token")
    
    if (savedUser && savedToken) {
      setUser(JSON.parse(savedUser))
      apiClient.setToken(savedToken)
    }
    setIsLoading(false)
  }, [])

  const login = async (email: string, password: string) => {
    setIsLoading(true)
    try {
      // Use OAuth2PasswordRequestForm format for login
      const formData = new URLSearchParams()
      formData.append('username', email) // OAuth2 uses 'username' field for email
      formData.append('password', password)
      
      const response = await fetch(`http://127.0.0.1:8000/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: formData.toString()
      })
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        const errorMessage = errorData.detail || `HTTP ${response.status}`
        
        if (response.status === 401) {
          throw new Error("Invalid email or password. Please check your credentials and try again.")
        } else if (response.status === 422) {
          throw new Error("Please enter a valid email address.")
        } else {
          throw new Error(errorMessage)
        }
      }
      
      const tokenData = await response.json()
      
      // Store token
      localStorage.setItem('access_token', tokenData.access_token)
      apiClient.setToken(tokenData.access_token)
      
      // Get user info (we'll need to create an endpoint for this or decode from token)
      // For now, we'll use the email to create a basic user object
      const user: User = {
        id: 0, // We'll get this from a user info endpoint
        name: email.split('@')[0], // Temporary name from email
        email: email,
        home_currency: 'USD' // Default currency
      }
      
      setUser(user)
      localStorage.setItem("user", JSON.stringify(user))
    } catch (error: unknown) {
      if (error instanceof Error) {
        throw error
      }
      throw new Error("Login failed")
    } finally {
      setIsLoading(false)
    }
  }

  const register = async (name: string, email: string, password: string, home_currency: string = 'USD') => {
    setIsLoading(true)
    try {
      const userData = {
        name,
        email,
        password,
        home_currency
      }
      
      const response = await apiClient.post<{ id: number; name: string; email: string; home_currency: string }>('/auth/register', userData)
      
      // After successful registration, automatically log in
      const user: User = {
        id: response.id,
        name: response.name,
        email: response.email,
        home_currency: response.home_currency
      }
      
      setUser(user)
      localStorage.setItem("user", JSON.stringify(user))
    } catch (error: unknown) {
      const errorResponse = error as { response?: { status?: number; data?: { detail?: string } } }
      const status = errorResponse.response?.status
      const detail = errorResponse.response?.data?.detail
      
      let errorMessage = "Registration failed"
      
      if (status === 400) {
        errorMessage = "Please check your input. All fields are required and password must be at least 8 characters."
      } else if (status === 409) {
        errorMessage = "An account with this email already exists. Please try logging in instead."
      } else if (status === 422) {
        errorMessage = "Please enter a valid email address and ensure all fields are filled correctly."
      } else if (status === 500) {
        errorMessage = "Server error. Please try again later."
      } else if (detail) {
        errorMessage = detail
      }
      
      throw new Error(errorMessage)
    } finally {
      setIsLoading(false)
    }
  }

  const logout = () => {
    setUser(null)
    localStorage.removeItem("user")
    localStorage.removeItem("access_token")
    apiClient.setToken(null)
  }

  const value = {
    user,
    isAuthenticated: !!user,
    isLoading,
    login,
    register,
    logout
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

// Export the context for the hook
export { AuthContext }

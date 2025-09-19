import { Button } from "./ui/button"
import { 
  Menu, 
  Sun, 
  Moon, 
  Bell, 
  Search,
  Plus,
  LogOut
} from "lucide-react"
import { useTheme } from "@/store/ui"
import { useAuth } from "@/hooks/useAuth"
import { Input } from "./ui/input"

interface HeaderProps {
  onMobileMenuToggle: () => void
}

export function Header({ onMobileMenuToggle }: HeaderProps) {
  const { theme, toggleTheme } = useTheme()
  const auth = useAuth()
  const { user, logout } = auth || { user: null, logout: () => {} }

  return (
    <header className="flex h-16 items-center justify-between border-b border-border bg-card px-6">
      {/* Left side */}
      <div className="flex items-center gap-4">
        <Button
          variant="ghost"
          size="icon"
          className="lg:hidden"
          onClick={onMobileMenuToggle}
        >
          <Menu className="h-5 w-5" />
        </Button>
        
        {/* Search */}
        <div className="relative hidden md:block">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Search transactions, accounts..."
            className="pl-10 w-80"
          />
        </div>
      </div>
      
      {/* Right side */}
      <div className="flex items-center gap-2">
        {/* User info */}
        <div className="hidden sm:flex items-center gap-2 text-sm text-muted-foreground">
          <span>Welcome, {user?.name}</span>
        </div>
        
        {/* Quick add button */}
        <Button size="sm" className="hidden sm:flex">
          <Plus className="h-4 w-4 mr-2" />
          Add Transaction
        </Button>
        
        {/* Notifications */}
        <Button variant="ghost" size="icon">
          <Bell className="h-5 w-5" />
        </Button>
        
        {/* Theme toggle */}
        <Button
          variant="ghost"
          size="icon"
          onClick={toggleTheme}
        >
          {theme === "dark" ? (
            <Sun className="h-5 w-5" />
          ) : (
            <Moon className="h-5 w-5" />
          )}
        </Button>
        
        {/* Logout button */}
        <Button
          variant="ghost"
          size="icon"
          onClick={logout}
          title="Logout"
        >
          <LogOut className="h-5 w-5" />
        </Button>
      </div>
    </header>
  )
}

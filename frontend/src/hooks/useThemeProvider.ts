import { useContext } from "react"
import { ThemeProviderContext } from "@/contexts/ThemeContext"

export const useThemeProvider = () => {
  const context = useContext(ThemeProviderContext)

  if (context === undefined)
    throw new Error("useThemeProvider must be used within a ThemeProvider")

  return context
}

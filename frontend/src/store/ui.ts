import { create } from "zustand"
import { persist } from "zustand/middleware"

interface UIState {
  // Theme
  theme: "dark" | "light"
  setTheme: (theme: "dark" | "light") => void
  toggleTheme: () => void
  
  // Sidebar
  sidebarCollapsed: boolean
  setSidebarCollapsed: (collapsed: boolean) => void
  toggleSidebar: () => void
  
  // Modals
  modals: Record<string, boolean>
  openModal: (modalId: string) => void
  closeModal: (modalId: string) => void
  closeAllModals: () => void
  
  // Notifications
  notifications: Array<{
    id: string
    type: "success" | "error" | "warning" | "info"
    title: string
    message?: string
    duration?: number
  }>
  addNotification: (notification: Omit<UIState["notifications"][0], "id">) => void
  removeNotification: (id: string) => void
  clearNotifications: () => void
  
  // Loading states
  loading: Record<string, boolean>
  setLoading: (key: string, loading: boolean) => void
  
  // User preferences
  preferences: {
    currency: string
    dateFormat: string
    numberFormat: string
    timezone: string
  }
  updatePreferences: (preferences: Partial<UIState["preferences"]>) => void
  
  // Table settings
  tableSettings: Record<string, {
    pageSize: number
    sortBy?: string
    sortOrder?: "asc" | "desc"
    filters?: Record<string, unknown>
  }>
  updateTableSettings: (tableId: string, settings: Partial<UIState["tableSettings"][string]>) => void
}

export const useUIStore = create<UIState>()(
  persist(
    (set) => ({
      // Theme
      theme: "dark",
      setTheme: (theme) => set({ theme }),
      toggleTheme: () => set((state) => ({ theme: state.theme === "dark" ? "light" : "dark" })),
      
      // Sidebar
      sidebarCollapsed: false,
      setSidebarCollapsed: (collapsed) => set({ sidebarCollapsed: collapsed }),
      toggleSidebar: () => set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed })),
      
      // Modals
      modals: {},
      openModal: (modalId) => set((state) => ({
        modals: { ...state.modals, [modalId]: true }
      })),
      closeModal: (modalId) => set((state) => ({
        modals: { ...state.modals, [modalId]: false }
      })),
      closeAllModals: () => set({ modals: {} }),
      
      // Notifications
      notifications: [],
      addNotification: (notification) => set((state) => ({
        notifications: [
          ...state.notifications,
          { ...notification, id: Math.random().toString(36).substr(2, 9) }
        ]
      })),
      removeNotification: (id) => set((state) => ({
        notifications: state.notifications.filter(n => n.id !== id)
      })),
      clearNotifications: () => set({ notifications: [] }),
      
      // Loading states
      loading: {},
      setLoading: (key, loading) => set((state) => ({
        loading: { ...state.loading, [key]: loading }
      })),
      
      // User preferences
      preferences: {
        currency: "USD",
        dateFormat: "MMM dd, yyyy",
        numberFormat: "en-US",
        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
      },
      updatePreferences: (preferences) => set((state) => ({
        preferences: { ...state.preferences, ...preferences }
      })),
      
      // Table settings
      tableSettings: {},
      updateTableSettings: (tableId, settings) => set((state) => ({
        tableSettings: {
          ...state.tableSettings,
          [tableId]: { ...state.tableSettings[tableId], ...settings }
        }
      })),
    }),
    {
      name: "ui-store",
      partialize: (state) => ({
        theme: state.theme,
        sidebarCollapsed: state.sidebarCollapsed,
        preferences: state.preferences,
        tableSettings: state.tableSettings,
      }),
    }
  )
)

// Selectors for common use cases - using shallow equality to prevent infinite loops

export const useTheme = () => {
  const theme = useUIStore((state) => state.theme)
  const setTheme = useUIStore((state) => state.setTheme)
  const toggleTheme = useUIStore((state) => state.toggleTheme)
  return { theme, setTheme, toggleTheme }
}

export const useSidebar = () => {
  const collapsed = useUIStore((state) => state.sidebarCollapsed)
  const setCollapsed = useUIStore((state) => state.setSidebarCollapsed)
  const toggle = useUIStore((state) => state.toggleSidebar)
  return { collapsed, setCollapsed, toggle }
}

export const useNotifications = () => {
  const notifications = useUIStore((state) => state.notifications)
  const addNotification = useUIStore((state) => state.addNotification)
  const removeNotification = useUIStore((state) => state.removeNotification)
  const clearNotifications = useUIStore((state) => state.clearNotifications)
  return { notifications, addNotification, removeNotification, clearNotifications }
}

export const usePreferences = () => {
  const preferences = useUIStore((state) => state.preferences)
  const updatePreferences = useUIStore((state) => state.updatePreferences)
  return { preferences, updatePreferences }
}

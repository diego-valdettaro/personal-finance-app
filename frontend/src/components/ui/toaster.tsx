import { useNotifications } from "@/store/ui"
import { X } from "lucide-react"
import { useEffect } from "react"
import { Button } from "./button"

export function Toaster() {
  const { notifications, removeNotification } = useNotifications()

  useEffect(() => {
    notifications.forEach((notification) => {
      if (notification.duration && notification.duration > 0) {
        const timer = setTimeout(() => {
          removeNotification(notification.id)
        }, notification.duration)

        return () => clearTimeout(timer)
      }
    })
  }, [notifications, removeNotification])

  if (notifications.length === 0) return null

  return (
    <div className="fixed top-4 right-4 z-50 flex flex-col gap-2">
      {notifications.map((notification) => (
        <div
          key={notification.id}
          className={`
            flex items-center gap-3 rounded-lg border p-4 shadow-lg backdrop-blur-sm
            ${
              notification.type === "success"
                ? "border-positive/20 bg-positive/10 text-positive-foreground"
                : notification.type === "error"
                ? "border-negative/20 bg-negative/10 text-negative-foreground"
                : notification.type === "warning"
                ? "border-warning/20 bg-warning/10 text-warning-foreground"
                : "border-muted-foreground/20 bg-muted/10 text-muted-foreground"
            }
          `}
        >
          <div className="flex-1">
            <div className="font-medium">{notification.title}</div>
            {notification.message && (
              <div className="text-sm opacity-90">{notification.message}</div>
            )}
          </div>
          <Button
            variant="ghost"
            size="icon"
            className="h-6 w-6"
            onClick={() => removeNotification(notification.id)}
          >
            <X className="h-4 w-4" />
          </Button>
        </div>
      ))}
    </div>
  )
}

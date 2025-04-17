"use client"

import { cn } from "@/lib/utils"

export type StatusType = "live" | "upcoming" | "completed" | "new"

interface StatusBadgeProps {
  status: StatusType
  className?: string
}

export function StatusBadge({ status, className }: StatusBadgeProps) {
  // Define status configurations
  const statusConfig = {
    live: {
      color: "bg-green-400",
      text: "text-green-400", 
      label: "Live Call",
      animate: "animate-pulse"
    },
    upcoming: {
      color: "bg-yellow-400",
      text: "text-yellow-400",
      label: "Upcoming",
      animate: ""
    },
    completed: {
      color: "bg-gray-400", 
      text: "text-gray-400",
      label: "Completed",
      animate: ""
    },
    new: {
      color: "bg-pink-500",
      text: "text-pink-500",
      label: "NEW",
      animate: ""
    }
  }

  // Get configuration for current status
  const config = statusConfig[status]

  // If status is 'new', render a different style of badge
  if (status === "new") {
    return (
      <span className={cn(
        "px-3 py-1 bg-pink-500/20 text-pink-500 text-xs rounded-full font-bold",
        className
      )}>
        {config.label}
      </span>
    )
  }

  // Otherwise render the status dot + text label
  return (
    <div className={cn("flex items-center space-x-2", className)}>
      <span className={cn(
        "w-2 h-2 rounded-full", 
        config.color, 
        config.animate
      )}></span>
      <span className={cn(
        "text-sm font-medium", 
        config.text
      )}>
        {config.label}
      </span>
    </div>
  )
} 
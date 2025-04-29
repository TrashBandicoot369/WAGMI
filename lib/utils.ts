import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

/**
 * Formats a date string or Firestore timestamp to a human-readable format
 * Handles both string dates and Firestore timestamp objects with seconds/nanoseconds
 * Example: "Apr 17, 2025 – 4:20 PM"
 */
export function formatDate(timestamp: any): string {
  // Handle Firestore timestamps (which have seconds and nanoseconds)
  if (timestamp?.seconds) {
    const date = new Date(timestamp.seconds * 1000)
    return date.toLocaleString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
      hour: "numeric",
      minute: "2-digit",
    }).replace(',', ' –')
  }

  // Handle regular string dates as before
  if (typeof timestamp === 'string') {
    const date = new Date(timestamp)
    
    // Check if the date is valid
    if (isNaN(date.getTime())) {
      return timestamp // Return the original string if we can't parse it
    }
    
    // Format the date using Intl.DateTimeFormat
    return new Intl.DateTimeFormat('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
      hour12: true
    }).format(date).replace(',', ' –')
  }

  return "Invalid date"
}

/**
 * Formats a market cap value to a readable format with appropriate suffixes
 * Examples: 1.5M, 25K, 3.2B
 */
export function formatMarketCap(value: number): string {
  if (!value) return "0";
  
  if (value >= 1_000_000_000) {
    return (value / 1_000_000_000).toFixed(1) + 'B';
  } 
  
  if (value >= 1_000_000) {
    return (value / 1_000_000).toFixed(1) + 'M';
  }
  
  if (value >= 1_000) {
    return (value / 1_000).toFixed(1) + 'K';
  }
  
  return value.toFixed(0);
}

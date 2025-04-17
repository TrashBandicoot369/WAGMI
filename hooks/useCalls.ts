"use client"

import { useState, useEffect } from "react"
import type { TokenData } from "@/types"

export function useCalls() {
  const [calls, setCalls] = useState<TokenData[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    // Simulate async data fetching
    const fetchCalls = async () => {
      try {
        setLoading(true)
        // In a real implementation, this would be a Firebase query
        // For now, we'll just use a timeout to simulate network latency
        await new Promise(resolve => setTimeout(resolve, 800))
        
        // Mock data - in production this would come from Firestore
        const mockCalls: TokenData[] = [
          {
            id: "1",
            tokenName: "PEPE",
            timestamp: "2025-04-17T16:20:00Z",
            dexLink: "https://dexscreener.com/ethereum/pepe",
            isNew: true,
            status: "live",
          },
          {
            id: "2",
            tokenName: "WOJAK",
            timestamp: "2025-04-17T15:15:00Z",
            dexLink: "https://dexscreener.com/ethereum/wojak",
            isNew: true,
            status: "live",
          },
          {
            id: "3",
            tokenName: "DEGEN",
            timestamp: "2025-04-17T14:30:00Z",
            dexLink: "https://dexscreener.com/ethereum/degen",
            status: "live",
          },
          {
            id: "4",
            tokenName: "SHIB",
            timestamp: "2025-04-17T13:45:00Z",
            dexLink: "https://dexscreener.com/ethereum/shib",
            status: "completed",
          },
          {
            id: "5",
            tokenName: "FLOKI",
            timestamp: "2025-04-17T12:30:00Z",
            dexLink: "https://dexscreener.com/ethereum/floki",
            status: "completed",
          },
          {
            id: "6",
            tokenName: "BONK",
            timestamp: "2025-04-17T11:15:00Z",
            dexLink: "https://dexscreener.com/solana/bonk",
            status: "completed",
          },
        ]

        setCalls(mockCalls)
        setLoading(false)
      } catch (err) {
        setError("Failed to fetch calls")
        setLoading(false)
        console.error("Error fetching calls:", err)
      }
    }

    fetchCalls()

    // In a real implementation, you might set up a Firebase listener here
    // And return the unsubscribe function for cleanup
    return () => {
      // Cleanup function would go here (if needed)
    }
  }, [])

  return { calls, loading, error }
} 
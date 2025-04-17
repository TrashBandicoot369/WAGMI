"use client"

import { useEffect, useState } from "react"
import { db } from "@/lib/firebase"
import { collection, onSnapshot, query, orderBy } from "firebase/firestore"
import { TokenData } from "@/types"

// Filler calls data to bypass Firebase
const fillerCalls: TokenData[] = [
  {
    id: "1",
    token: "BONK",
    timestamp: new Date("2025-04-17T16:20:00Z"),
    status: "LIVE" as const,
    dexUrl: "https://dexscreener.com/solana/bonk"
  },
  {
    id: "2",
    token: "WAGMI",
    timestamp: new Date("2025-04-17T15:45:00Z"),
    status: "COMPLETED" as const,
    dexUrl: "https://dexscreener.com/solana/wagmi"
  },
  {
    id: "3",
    token: "PEPE2",
    timestamp: new Date("2025-04-17T14:30:00Z"),
    status: "NEW" as const,
    dexUrl: "https://dexscreener.com/ethereum/pepe2"
  }
]

export function useCalls(): TokenData[] {
  const [calls, setCalls] = useState<TokenData[]>(fillerCalls)

  // Comment out Firebase integration for now
  /*
  useEffect(() => {
    // Only run if db is available (client-side)
    if (!db) return

    const q = query(collection(db, "calls"), orderBy("timestamp", "desc"))
    const unsubscribe = onSnapshot(q, (snapshot) => {
      const data = snapshot.docs.map((doc) => {
        return {
          id: doc.id,
          ...doc.data()
        } as TokenData
      })
      setCalls(data)
    })

    return () => unsubscribe()
  }, [])
  */

  return calls
} 
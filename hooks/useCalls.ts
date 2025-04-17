"use client"

import { useEffect, useState } from "react"
import { db } from "@/lib/firebase"
import { collection, onSnapshot, query, orderBy } from "firebase/firestore"
import { TokenData } from "@/types"

export function useCalls() {
  const [calls, setCalls] = useState<TokenData[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    // Only run on client side
    if (typeof window === 'undefined') return

    try {
      setLoading(true)
      const q = query(collection(db, "calls"), orderBy("timestamp", "desc"))
      const unsubscribe = onSnapshot(q, (snapshot) => {
        const data = snapshot.docs.map((doc) => ({
          id: doc.id,
          ...doc.data()
        })) as TokenData[]
        setCalls(data)
        setLoading(false)
      }, (err) => {
        console.error("Error fetching calls:", err)
        setError("Failed to fetch calls")
        setLoading(false)
      })

      return () => unsubscribe()
    } catch (err) {
      console.error("Error setting up Firebase listener:", err)
      setError("Failed to connect to database")
      setLoading(false)
      return () => {}
    }
  }, [])

  return { calls, loading, error }
} 
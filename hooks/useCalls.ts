"use client"

import { useEffect, useState } from "react"
import { db } from "@/lib/firebase"
import { collection, onSnapshot, query, orderBy } from "firebase/firestore"
import { TokenData } from "@/types"

export function useCalls(): TokenData[] {
  const [calls, setCalls] = useState<TokenData[]>([])

  useEffect(() => {
    if (!db) return

    const q = query(collection(db, "calls"), orderBy("timestamp", "desc"))
    
    const unsubscribe = onSnapshot(q, (snapshot) => {
      const data = snapshot.docs.map((doc) => {
        const docData = doc.data() as Omit<TokenData, 'id'>
        return {
          id: doc.id,
          ...docData
        }
      })
      console.log("🔥 Firestore snapshot:", data)
      setCalls(data)
    })

    return () => unsubscribe()
  }, [])

  return calls
} 
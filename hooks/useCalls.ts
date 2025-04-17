"use client"

import { useEffect, useState } from "react"
import { db } from "@/lib/firebase"
import { collection, onSnapshot, query, orderBy } from "firebase/firestore"
import { TokenData } from "@/types"

export function useCalls(): TokenData[] {
  const [calls, setCalls] = useState<TokenData[]>([])

  useEffect(() => {
    const q = query(collection(db, "calls"), orderBy("timestamp", "desc"))
    const unsubscribe = onSnapshot(q, (snapshot) => {
      const data = snapshot.docs.map((doc) => ({
        id: doc.id,
        ...doc.data()
      })) as TokenData[]
      setCalls(data)
    })

    return () => unsubscribe()
  }, [])

  return calls
} 
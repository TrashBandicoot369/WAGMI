"use client"

import { useEffect, useState } from "react"
import { db } from "@/lib/firebase"
import { collection, getDocs } from "firebase/firestore"
import { TokenData } from "@/types"

export function useCalls(): TokenData[] {
  const [calls, setCalls] = useState<TokenData[]>([])

  useEffect(() => {
    async function fetchData() {
      if (!db) {
        console.error("🔥 Firestore not initialized")
        return
      }

      try {
        const snapshot = await getDocs(collection(db, "calls"))
        const data = snapshot.docs.map((doc) => {
          const docData = doc.data() as Omit<TokenData, 'id'>
          return {
            id: doc.id,
            ...docData
          }
        })
        console.log("✅ Fetched Firestore docs:", data)
        setCalls(data)
      } catch (err) {
        console.error("❌ Error fetching from Firestore:", err)
      }
    }

    fetchData()
  }, [])

  return calls
} 
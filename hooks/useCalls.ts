"use client"

import { useEffect, useState } from "react"
import { db } from "@/lib/firebase"
import { collection, query, orderBy, onSnapshot, limit, Unsubscribe } from "firebase/firestore"
import { TokenData } from "@/types"

export function useCalls(maxCalls: number = 100): {
  calls: TokenData[];
  error: Error | null;
  loading: boolean;
  connected: boolean;
} {
  const [calls, setCalls] = useState<TokenData[]>([])
  const [error, setError] = useState<Error | null>(null)
  const [loading, setLoading] = useState<boolean>(true)
  const [connected, setConnected] = useState<boolean>(false)

  useEffect(() => {
    let unsubscribe: Unsubscribe | null = null;
    let connectionTimeout: NodeJS.Timeout;
    
    async function setupRealTimeListener() {
      if (!db) {
        setError(new Error("Firestore not initialized"));
        setLoading(false);
        return;
      }

      try {
        // Set a timeout to detect potential connection issues
        connectionTimeout = setTimeout(() => {
          if (loading && !connected) {
            setError(new Error("Connection timeout - could not connect to Firestore"));
            setLoading(false);
          }
        }, 10000);

        // Create a query for the most recent calls
        const q = query(
          collection(db, "calls"),
          orderBy("timestamp", "desc"),
          limit(maxCalls)
        );

        // Listen for real-time updates
        unsubscribe = onSnapshot(q, (snapshot) => {
          // Clear timeout as we got a response
          clearTimeout(connectionTimeout);
          setConnected(true);
          setLoading(false);
          setError(null);
          
          const data: TokenData[] = [];
          
          snapshot.docs.forEach((doc) => {
            const docData = doc.data();

            // Consistently use symbol or token field for the token name
            const token = docData.token || docData.symbol || "UNKNOWN";
            const dexUrl = docData.dexUrl || docData.dexurl || "";
            const timestamp = docData.timestamp;

            // Skip if essential fields are missing
            if (!token || !dexUrl || !timestamp) {
              console.warn(`⚠️ Skipping doc ${doc.id} due to missing fields`, { token, dexUrl, timestamp });
              return;
            }

            // Extract numeric fields with type safety
            const safeNumber = (value: any): number | undefined => {
              if (value === undefined || value === null) return undefined;
              return typeof value === 'string' ? parseFloat(value) : value;
            };

            // Prepare token data
            data.push({
              id: doc.id,
              token,
              dexUrl,
              timestamp,
              status: docData.status || "LIVE",
              isNew: docData.isNew || false,
              
              // Market data fields matching the Firestore screenshot
              marketCap: safeNumber(docData.marketCap),
              volume24h: safeNumber(docData.volume24h) || safeNumber(docData.volume), // Support both field names
              initialMarketCap: safeNumber(docData.initialMarketCap),
              athMarketCap: safeNumber(docData.athMarketCap),
              
              // Percentage changes from both possible field names
              percentChange24h: safeNumber(docData.percentChange24h) || safeNumber(docData.capChange),
              
              // Contract information
              contract: docData.contract,
              chain: docData.chain || "solana",
              
              // Timestamps
              lastRefreshed: docData.lastRefreshed,
              updated: docData.updated,
              
              // Flag for important calls
              shotCaller: docData.shotCaller || false,
              
              // Social links
              twitter: docData.twitter,
              socials: docData.socials,
              
              // Additional fields
              confidence: safeNumber(docData.confidence)
            });
          });

          console.log(`✅ Loaded ${data.length} valid calls from Firestore (real-time)`);
          setCalls(data);
        }, (err) => {
          clearTimeout(connectionTimeout);
          console.error("❌ Error in Firestore snapshot:", err);
          setError(err);
          setLoading(false);
          setConnected(false);
        });
        
      } catch (err: any) {
        clearTimeout(connectionTimeout);
        console.error("❌ Error setting up Firestore listener:", err);
        setError(err);
        setLoading(false);
        setConnected(false);
      }
    }

    setupRealTimeListener();

    // Cleanup function to unsubscribe when component unmounts
    return () => {
      if (unsubscribe) {
        unsubscribe();
      }
      clearTimeout(connectionTimeout);
    }
  }, [maxCalls]); // Dependency on maxCalls

  return { calls, error, loading, connected };
}

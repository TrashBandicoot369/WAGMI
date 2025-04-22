"use client"

import { useEffect, useState } from "react"
import { collection, query, orderBy, limit, onSnapshot } from "firebase/firestore"
import { TokenData } from "@/types"
import { getFirebaseDb } from "@/lib/firebase-unified"

export default function TickerMarquee() {
  const [topGainers, setTopGainers] = useState<{ symbol: string; gain: number; dexUrl: string }[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const db = getFirebaseDb();
    if (!db) {
      console.error("🔥 Firestore not initialized for ticker")
      return
    }

    const calculateGainPercentage = (token: any) => {
      const initialCap = typeof token.initialMarketCap === "string" 
        ? parseFloat(token.initialMarketCap) 
        : token.initialMarketCap;
      
      const athCap = typeof token.athMarketCap === "string" 
        ? parseFloat(token.athMarketCap) 
        : token.athMarketCap;
      
      if (!initialCap || !athCap || initialCap <= 0 || athCap <= 0) return 0;
      
      return Math.round(((athCap - initialCap) / initialCap) * 100);
    };

    // Query to get tokens with initialMarketCap and athMarketCap
    const q = query(
      collection(db, "calls"),
      orderBy("timestamp", "desc"),
      limit(50) // Get more tokens to filter for those with gain data
    );

    const unsubscribe = onSnapshot(q, (snapshot) => {
      setIsLoading(true);
      console.log("📡 Ticker snapshot triggered:", snapshot.size);
      
      // Use a Map to prevent duplicate symbols, keeping only the highest gain for each symbol
      const symbolDataMap = new Map<string, { gain: number; dexUrl: string }>();
      
      snapshot.docs.forEach(doc => {
        const data = doc.data();
        const symbol = data.symbol || "UNKNOWN";
        if (symbol === "UNKNOWN") return;
        
        const gain = calculateGainPercentage(data);
        if (gain <= 0) return;
        
        const dexUrl = data.dexUrl || data.dexurl || "";
        
        // If this symbol doesn't exist in map or has a higher gain than existing entry
        if (!symbolDataMap.has(symbol) || gain > symbolDataMap.get(symbol)!.gain) {
          symbolDataMap.set(symbol, { gain, dexUrl });
        }
      });
      
      // Convert map to array and sort by gain
      const tokensWithGains = Array.from(symbolDataMap.entries())
        .map(([symbol, data]) => ({ 
          symbol, 
          gain: data.gain, 
          dexUrl: data.dexUrl 
        }))
        .sort((a, b) => b.gain - a.gain) // Sort by highest gain first
        .slice(0, 15); // Take top 15 gainers
      
      setTopGainers(tokensWithGains);
      setIsLoading(false);
    });

    return () => unsubscribe();
  }, []);

  if (isLoading || topGainers.length === 0) {
    return <div className="h-8"></div>;
  }

  // Double the items to create seamless loop
  const tickerItems = [...topGainers, ...topGainers];

  return (
    <div className="w-full overflow-hidden py-1.5">
      <div className="animate-marquee inline-block whitespace-nowrap">
        {tickerItems.map((token, index) => (
          <a 
            key={index} 
            href={token.dexUrl} 
            target="_blank" 
            rel="noopener noreferrer"
            className="inline-flex items-center mx-4 hover:opacity-80 transition-opacity cursor-pointer"
            onClick={(e) => {
              if (!token.dexUrl) {
                e.preventDefault();
              }
            }}
          >
            <span className="font-bold text-white">${token.symbol}</span>
            <span className="ml-1 text-green-400 font-medium">+{token.gain}%</span>
            {token.gain >= 100 && (
              <span className="ml-1 px-1.5 py-0.5 bg-green-500/30 text-green-300 text-xs font-bold rounded-full">
                {Math.round(token.gain / 100 + 1)}x
              </span>
            )}
          </a>
        ))}
      </div>
    </div>
  );
} 
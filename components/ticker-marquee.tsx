"use client"

import { useEffect, useRef, useState } from "react"
import { collection, query, orderBy, limit, onSnapshot } from "firebase/firestore"
import { TokenData } from "@/types"
import { getFirebaseDb } from "@/lib/firebase-unified"

export default function TickerMarquee() {
  const [topGainers, setTopGainers] = useState<{ symbol: string; gain: number; dexUrl: string }[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const contentRef = useRef<HTMLDivElement>(null)
  const [contentWidth, setContentWidth] = useState(0)

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
      limit(100) // Get more tokens to filter for those with gain data
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
        .slice(0, 20); // Take top 20 gainers
      
      setTopGainers(tokensWithGains);
      setIsLoading(false);
    });

    return () => unsubscribe();
  }, []);

  // Measure the width of the content for pixel-perfect animation
  useEffect(() => {
    if (contentRef.current) {
      setContentWidth(contentRef.current.offsetWidth);
    }
  }, [topGainers]);

  const scrollingItems = Array(4).fill(topGainers).flat();

  if (isLoading || topGainers.length === 0) {
    return <div className="h-8"></div>;
  }

  return (
    <div className="overflow-hidden w-full">
      <div className="flex whitespace-nowrap animate-marquee">
        {scrollingItems.map((token, index) => (
          <a
            key={index}
            href={token.dexUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 px-4"
          >
            <span className="text-white font-bold">${token.symbol}</span>
            <span className="text-green-400 font-medium">+{token.gain}%</span>
            {token.gain >= 100 && (
              <span className="text-green-300 text-xs font-bold px-2 py-0.5 bg-green-500/30 rounded-full">
                {Math.round(token.gain / 100 + 1)}x
              </span>
            )}
          </a>
        ))}
      </div>
    </div>
  );
} 
"use client"

import { useState, useEffect } from "react"
import Link from "next/link"
import { Twitter, TextIcon as Telegram } from "lucide-react"
import { collection, query, orderBy, limit, onSnapshot } from "firebase/firestore"
import { getFirebaseDb } from "@/lib/firebase-unified"

export default function Header() {
  const [scrolled, setScrolled] = useState(false)
  const [topGainers, setTopGainers] = useState<{ symbol: string; gain: number; dexUrl: string }[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 10)
    }

    window.addEventListener("scroll", handleScroll)
    return () => window.removeEventListener("scroll", handleScroll)
  }, [])

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

  return (
    <header
      className={`sticky top-0 z-50 w-full transition-all duration-300 ${
        scrolled
          ? "bg-white/20 backdrop-blur-lg shadow-lg shadow-green-500/10"
          : "bg-transparent"
      }`}
    >
      {/* Top section with logo and social icons */}
      <div className="relative">
        <div className="container mx-auto px-4 py-2 flex flex-col items-center">
          {/* Centered WAGMI logo at 3x size */}
          <div className="w-full flex flex-col items-center mb-0">
            <img 
              src="/wagmi.png" 
              alt="WAGMI" 
              className="h-auto w-auto transform scale-300"
              style={{ maxWidth: '300px', transform: 'scale(3)', marginTop: '30px', marginBottom: '5px' }}
            />
            {/* Added tagline in green */}
            <p className="text-green-400 font-bold text-2xl -mt-4 mb-1 text-center">
              [We're All Gonna Make It]
            </p>
          </div>
          
          {/* Social media icons in the corner */}
          <div className="absolute top-2 right-4 flex items-center space-x-3">
            <Link href="#" className="text-white hover:text-green-400 transition-colors">
              <Twitter size={18} />
            </Link>
            <Link href="#" className="text-white hover:text-green-400 transition-colors">
              <Telegram size={18} />
            </Link>
          </div>
        </div>
      </div>
      
      {/* Full-width ticker marquee outside any container */}
      <div className="w-full overflow-hidden border-t border-b border-white/20 py-1 bg-black/20 backdrop-blur-sm">
        {!isLoading && topGainers.length > 0 ? (
          <div className="whitespace-nowrap overflow-hidden w-full">
            {/* Scrolling content */}
            <div 
              className="inline-block whitespace-nowrap animate-marquee"
              style={{ display: 'inline-block', whiteSpace: 'nowrap' }}
            >
              {/* Double the items to create seamless loop */}
              {[...topGainers, ...topGainers].map((token, index) => (
                <a 
                  key={index} 
                  href={token.dexUrl} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="inline-flex items-center mx-2 hover:opacity-80 transition-opacity cursor-pointer"
                >
                  <span className="font-bold text-white">${token.symbol}</span>
                  <span className="ml-1 text-green-400 font-medium">+{token.gain}%</span>
                  {token.gain >= 100 && (
                    <span className="ml-1 px-1 py-0.5 bg-green-500/30 text-green-300 text-xs font-bold rounded-full">
                      {Math.round(token.gain / 100 + 1)}x
                    </span>
                  )}
                </a>
              ))}
            </div>
          </div>
        ) : (
          <div className="text-center text-white/50 text-sm">Loading top tokens...</div>
        )}
      </div>
    </header>
  )
}

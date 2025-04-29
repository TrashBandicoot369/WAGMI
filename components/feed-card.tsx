"use client"

import React from "react"
import { motion } from "framer-motion"
import type { TokenData } from "@/types"
import { StatusBadge, type StatusType } from "./ui/StatusBadge"
import { DexButton } from "./ui/DexButton"
import { formatDate, formatMarketCap } from "@/lib/utils"

// Map from TokenData status to StatusType
const mapStatus = (status: "LIVE" | "COMPLETED" | "NEW"): StatusType => {
  const statusMap: Record<"LIVE" | "COMPLETED" | "NEW", StatusType> = {
    "LIVE": "live",
    "COMPLETED": "completed",
    "NEW": "new"
  }
  return statusMap[status]
}

// Calculate multiplier based on percentage gain
const calculateMultiplier = (initialMarketCap?: number, athMarketCap?: number): number | null => {
  if (!initialMarketCap || !athMarketCap || initialMarketCap <= 0) return null;
  
  const multiplier = athMarketCap / initialMarketCap;
  return multiplier >= 2 ? Math.round(multiplier) : null;
}

// Calculate percentage gain from initial to ATH
const calculatePercentageGain = (initialMarketCap?: number, athMarketCap?: number): number | null => {
  if (!initialMarketCap || !athMarketCap || initialMarketCap <= 0) return null;
  
  return ((athMarketCap - initialMarketCap) / initialMarketCap) * 100;
}

// Calculate ATH to current market cap percentage gain
const calculateAthPercentGain = (currentMarketCap?: number, athMarketCap?: number): number | null => {
  if (!currentMarketCap || !athMarketCap || currentMarketCap <= 0) return null;
  
  // This calculates how much higher ATH is from current (or how much lower if negative)
  return ((athMarketCap / currentMarketCap) - 1) * 100;
}

// Calculate percentage changes
const calculatePercentChange = (current: number, previous: number): number => {
  return ((current - previous) / previous) * 100;
};

// Calculate market cap change from initial
const totalChange = (initialMarketCap?: number, marketCap?: number): number => {
  if (!initialMarketCap || !marketCap || initialMarketCap <= 0) return 0;
  
  return calculatePercentChange(marketCap, initialMarketCap);
};

// Calculate ATH gain percentage
const calculateAthGain = (initialCap?: number, athCap?: number): number => {
  if (!initialCap || !athCap || initialCap <= 0 || athCap <= 0) return 0;
  return Math.round(((athCap - initialCap) / initialCap) * 100);
};

export default function FeedCard({
  id,
  token,
  timestamp,
  dexUrl,
  isNew,
  status,
  marketCap,
  initialMarketCap,
  volume24h,
  contract,
  athMarketCap,
  athGainPercent,
}: TokenData) {
  // Set fallback values for tokens with missing data
  const safeMarketCap = marketCap || 1000; // Minimum fallback value if no market cap
  const safeInitialMarketCap = initialMarketCap || safeMarketCap;
  const safeVolume = volume24h || 0;
  const safeAthMarketCap = athMarketCap || safeMarketCap;
  
  // Calculate percentage with color and sign
  const formatPercentage = (percent: number | undefined) => {
    if (percent === undefined || percent === null) return '';
    const sign = percent >= 0 ? '+' : '';
    return `(${sign}${percent.toFixed(0)}%)`;
  };

  // For UNKNOWN tokens, we'll show a placeholder with the contract
  const displayToken = token === "UNKNOWN" && contract ? 
    `${contract.substring(0, 5)}...${contract.substring(contract.length - 5)}` : 
    token;
  
  const isUnknownToken = token === "UNKNOWN";
  const isNewToken = isNew || (!marketCap && timestamp);

  return (
    <motion.div 
      whileHover={{ scale: 1.03, y: -5 }} 
      className={`w-full px-4 rounded-xl overflow-hidden relative transition-transform duration-200 hover:shadow-[0_0_12px_rgba(230,0,122,0.25)] ${isUnknownToken ? 'opacity-80' : ''}`}
    >
      {/* Card background with glassmorphism */}
      <div className={`absolute inset-0 ${isUnknownToken ? 'bg-[#3a2839]/80' : 'bg-[#a73967]/80'} backdrop-blur-md border border-white/10 rounded-xl`}></div>

      {/* Card content */}
      <div className="relative z-10 p-6">
        <div className="flex justify-between items-center mb-2">
          <h3 className="text-2xl font-bold text-white">
            {isUnknownToken ? (
              <span className="flex items-center">
                {displayToken} <span className="ml-2 text-xs bg-yellow-600 text-white px-2 py-1 rounded-md">Resolving</span>
              </span>
            ) : (
              `$${token}`
            )}
          </h3>
        </div>

        <p className="text-white/70 text-sm mb-4">{formatDate(timestamp)}</p>
        
        {/* Market Cap with change percentage */}
        <div className="flex items-start gap-2 mb-2">
          <span role="img" aria-label="money bag" className="text-yellow-300 mt-1">💰</span>
          <p className="text-white/80 text-sm">
            Market Cap: {!marketCap && isUnknownToken ? (
              <span className="text-white/50">Resolving...</span>
            ) : (
              <span className="text-white">
                ${formatMarketCap(safeMarketCap)}
                <span className={totalChange(initialMarketCap, marketCap) >= 0 ? "text-green-400 ml-1" : "text-red-400 ml-1"}>
                  {formatPercentage(totalChange(initialMarketCap, marketCap))}
                </span>
              </span>
            )}
          </p>
        </div>
        
        {/* Initial Market Cap */}
        <div className="flex items-start gap-2 mb-2">
          <span role="img" aria-label="trophy" className="text-yellow-300 mt-1">🏆</span>
          <p className="text-white/80 text-sm">
            Initial Market Cap: {!initialMarketCap && isUnknownToken ? (
              <span className="text-white/50">Resolving...</span>
            ) : (
              <span className="text-white">
                ${formatMarketCap(safeInitialMarketCap)}
              </span>
            )}
          </p>
        </div>
        
        {/* ATH Market Cap */}
        <div className="flex items-start gap-2 mb-2">
          <span role="img" aria-label="rocket" className="text-yellow-300 mt-1">🚀</span>
          <p className="text-white/80 text-sm">
            ATH Market Cap: {!athMarketCap ? (
              <span className="text-white/50">N/A</span>
            ) : (
              <span className="text-white">
                ${formatMarketCap(safeAthMarketCap)}
                {initialMarketCap && athMarketCap && (
                  <span className={calculateAthGain(initialMarketCap, athMarketCap) >= 0 ? "text-green-400 ml-1" : "text-red-400 ml-1"}>
                    ({calculateAthGain(initialMarketCap, athMarketCap) >= 0 ? "+" : ""}
                    {calculateAthGain(initialMarketCap, athMarketCap)}%
                    {calculateAthGain(initialMarketCap, athMarketCap) >= 100 ? ` x${Math.floor(calculateAthGain(initialMarketCap, athMarketCap) / 100)}` : ''}
                    )
                  </span>
                )}
              </span>
            )}
          </p>
        </div>
        
        {/* Volume with chart icon */}
        <div className="flex items-start gap-2 mb-5">
          <span role="img" aria-label="chart" className="text-blue-300 mt-1">📊</span>
          <p className="text-white/80 text-sm">
            Volume (24h): {!volume24h && isUnknownToken ? (
              <span className="text-white/50">Resolving...</span>
            ) : (
              <span className="text-white">
                ${formatMarketCap(safeVolume)}
              </span>
            )}
          </p>
        </div>

        {/* Dexscreener button */}
        <div className="flex justify-center">
          <a 
            href={dexUrl} 
            target="_blank" 
            rel="noopener noreferrer"
            className="text-center py-2 px-4 text-white/90 hover:text-white transition-colors"
          >
            View on Dexscreener
          </a>
        </div>
      </div>
    </motion.div>
  )
}

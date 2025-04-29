"use client"

import { motion } from "framer-motion"
import FeedCard from "./feed-card"
import { useCalls } from "@/hooks/useCalls"
import { db } from "@/lib/firebase"
import { useState, useEffect, useMemo } from "react"
import type { TokenData } from "@/types"

interface FeedSectionProps {
  title?: string
  description?: string
  showUnknown?: boolean
  showNoMarketCap?: boolean
}

export default function FeedSection({
  title = "Latest Alpha Drops",
  description = "Real-time calls from our expert team. Get in early, secure your gains.",
  showUnknown = true, // Default to showing unknown tokens
  showNoMarketCap = true, // Default to showing tokens without market cap
}: FeedSectionProps) {
  const { calls, error, loading, connected } = useCalls()
  
  // Filter calls based on parameters
  const validCalls = useMemo(() => {
    return calls.filter(call => {
      // Filter out tokens without market cap if showNoMarketCap is false
      if (!showNoMarketCap && (!call.marketCap || call.marketCap <= 0)) return false;
      
      // Filter out UNKNOWN tokens if showUnknown is false
      if (!showUnknown && call.token === "UNKNOWN") return false;
      
      return true;
    });
  }, [calls, showUnknown, showNoMarketCap]);

  return (
    <section className="pt-6 pb-10 md:pt-10 md:pb-16 relative">
      <div className="container mx-auto px-4 pb-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          viewport={{ once: true }}
          className="text-center mb-6"
        >
          <h2 className="text-2xl md:text-3xl font-bold uppercase tracking-wider mb-2 text-transparent bg-clip-text bg-gradient-to-r from-pink-500 to-green-400">
            {title}
          </h2>
          <p className="text-white/70 text-sm max-w-2xl mx-auto">{description}</p>
        </motion.div>

        {loading ? (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-pink-500 mb-4"></div>
            <p className="text-white/70">Loading latest calls...</p>
          </div>
        ) : error || !connected ? (
          <div className="text-center py-8 px-4 max-w-lg mx-auto bg-red-900/20 backdrop-blur-sm rounded-xl border border-red-500/20">
            <p className="text-red-300 mb-2">Unable to connect to Firestore.</p>
            <p className="text-white/70 text-sm mb-2">Please check your internet connection and try again later.</p>
            {error && (
              <p className="text-xs text-red-200/70 mt-2 bg-red-950/30 p-2 rounded">
                Error: {error.message}
              </p>
            )}
          </div>
        ) : validCalls.length > 0 ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {validCalls.map((call) => (
              <motion.div
                key={call.id}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
                viewport={{ once: true }}
              >
                <FeedCard {...call} />
              </motion.div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 px-4 max-w-lg mx-auto bg-gray-900/30 backdrop-blur-sm rounded-xl border border-white/10">
            <p className="text-white/70">No calls available at the moment.</p>
            <p className="text-white/50 text-sm mt-2">Check back soon for the latest crypto calls.</p>
          </div>
        )}
      </div>
    </section>
  )
}

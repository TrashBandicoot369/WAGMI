"use client"

import { motion } from "framer-motion"
import { ExternalLink } from "lucide-react"
import Link from "next/link"
import type { TokenData } from "@/types"

interface FeedCardProps {
  token: TokenData
}

export default function FeedCard({ token }: FeedCardProps) {
  const { tokenName, timestamp, dexLink, isNew, status } = token

  return (
    <motion.div whileHover={{ scale: 1.03, y: -5 }} className="rounded-xl overflow-hidden relative">
      {/* Card background with glassmorphism */}
      <div className="absolute inset-0 bg-white/20 backdrop-blur-md border border-white/30 rounded-xl"></div>

      {/* Glow effect on hover */}
      <motion.div
        initial={{ opacity: 0 }}
        whileHover={{ opacity: 1 }}
        className="absolute inset-0 bg-pink-500/10 rounded-xl shadow-[0_0_15px_rgba(230,0,122,0.3)] z-0"
      ></motion.div>

      {/* Card content */}
      <div className="relative z-10 p-6">
        <div className="flex justify-between items-start mb-4">
          <h3 className="text-2xl font-bold text-white">${tokenName}</h3>
          {isNew && <span className="px-3 py-1 bg-pink-500/20 text-pink-500 text-xs rounded-full font-bold">NEW</span>}
        </div>

        <p className="text-white/70 text-sm mb-6">{timestamp}</p>

        <div className="flex justify-between items-center">
          <div className="flex items-center space-x-2">
            {status === "live" && (
              <>
                <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse"></span>
                <span className="text-green-400 text-sm font-medium">Live Call</span>
              </>
            )}
            {status === "upcoming" && (
              <>
                <span className="w-2 h-2 rounded-full bg-yellow-400"></span>
                <span className="text-yellow-400 text-sm font-medium">Upcoming</span>
              </>
            )}
            {status === "completed" && (
              <>
                <span className="w-2 h-2 rounded-full bg-gray-400"></span>
                <span className="text-gray-400 text-sm font-medium">Completed</span>
              </>
            )}
          </div>

          <Link
            href={dexLink}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center text-sm text-white/80 hover:text-green-400 transition-colors"
          >
            <span className="mr-1">View on Dexscreener</span>
            <ExternalLink size={14} />
          </Link>
        </div>
      </div>
    </motion.div>
  )
}

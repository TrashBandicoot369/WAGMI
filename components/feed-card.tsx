"use client"

import { motion } from "framer-motion"
import type { TokenData } from "@/types"
import { StatusBadge } from "./ui/StatusBadge"
import { DexButton } from "./ui/DexButton"
import { formatDate } from "@/lib/utils"

interface FeedCardProps {
  token: TokenData
}

export default function FeedCard({ token }: FeedCardProps) {
  const { tokenName, timestamp, dexLink, isNew, status } = token

  return (
    <motion.div 
      whileHover={{ scale: 1.03, y: -5 }} 
      className="w-full h-full rounded-xl overflow-hidden relative"
    >
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
          {isNew && <StatusBadge status="new" />}
        </div>

        <p className="text-white/70 text-sm mb-6">{formatDate(timestamp)}</p>

        <div className="flex justify-between items-center">
          {status && <StatusBadge status={status} />}
          <DexButton link={dexLink} />
        </div>
      </div>
    </motion.div>
  )
}

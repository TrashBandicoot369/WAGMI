"use client"

import { motion } from "framer-motion"
import type { TokenData } from "@/types"
import { StatusBadge, type StatusType } from "./ui/StatusBadge"
import { DexButton } from "./ui/DexButton"
import { formatDate } from "@/lib/utils"

// Map from TokenData status to StatusType
const mapStatus = (status: "LIVE" | "COMPLETED" | "NEW"): StatusType => {
  const statusMap: Record<"LIVE" | "COMPLETED" | "NEW", StatusType> = {
    "LIVE": "live",
    "COMPLETED": "completed",
    "NEW": "new"
  }
  return statusMap[status]
}

export default function FeedCard({
  id,
  token,
  timestamp,
  dexUrl,
  isNew,
  status
}: TokenData) {
  return (
    <motion.div 
      whileHover={{ scale: 1.03, y: -5 }} 
      className="w-full px-4 rounded-xl overflow-hidden relative transition-transform duration-200 hover:scale-105 hover:shadow-[0_0_12px_rgba(0,255,0,0.25)]"
    >
      {/* Card background with glassmorphism */}
      <div className="absolute inset-0 bg-white/15 backdrop-blur-md border border-white/25 rounded-xl"></div>

      {/* Glow effect on hover */}
      <motion.div
        initial={{ opacity: 0 }}
        whileHover={{ opacity: 1 }}
        className="absolute inset-0 bg-pink-500/10 rounded-xl shadow-[0_0_15px_rgba(230,0,122,0.3)] z-0"
      ></motion.div>

      {/* Card content */}
      <div className="relative z-10 p-6">
        <div className="flex justify-between items-start mb-4">
          <h3 className="text-2xl font-bold text-white">${token}</h3>
          {isNew && <StatusBadge status="new" />}
        </div>

        <p className="text-white/70 text-sm mb-6">{formatDate(timestamp)}</p>

        <div className="flex justify-between items-center">
          {status && <StatusBadge status={mapStatus(status)} />}
          <DexButton link={dexUrl} />
        </div>
      </div>
    </motion.div>
  )
}

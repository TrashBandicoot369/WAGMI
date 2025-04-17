"use client"

import { motion } from "framer-motion"
import FeedCard from "./feed-card"
import type { TokenData } from "@/types"

interface FeedSectionProps {
  tokenData: TokenData[]
  title?: string
  description?: string
}

export default function FeedSection({
  tokenData,
  title = "Latest Alpha Drops",
  description = "Real-time calls from our expert team. Get in early, secure your gains.",
}: FeedSectionProps) {
  return (
    <section className="py-16 md:py-24 relative">
      <div className="container mx-auto px-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          viewport={{ once: true }}
          className="text-center mb-12"
        >
          <h2 className="text-3xl md:text-4xl font-bold uppercase tracking-wider mb-4 text-transparent bg-clip-text bg-gradient-to-r from-pink-500 to-green-400">
            {title}
          </h2>
          <p className="text-white/70 max-w-2xl mx-auto">{description}</p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {tokenData.map((token, index) => (
            <motion.div
              key={token.id}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              viewport={{ once: true }}
            >
              <FeedCard token={token} />
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}

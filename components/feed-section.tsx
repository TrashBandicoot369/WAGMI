"use client"

import { motion } from "framer-motion"
import FeedCard from "./feed-card"
import { useCalls } from "@/hooks/useCalls"

interface FeedSectionProps {
  title?: string
  description?: string
}

export default function FeedSection({
  title = "Latest Alpha Drops",
  description = "Real-time calls from our expert team. Get in early, secure your gains.",
}: FeedSectionProps) {
  const { calls, loading, error } = useCalls()

  return (
    <section className="pt-16 pb-20 md:pt-24 md:pb-24 relative">
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

        {loading && (
          <div className="flex justify-center py-20">
            <div className="animate-pulse flex space-x-2">
              <div className="h-3 w-3 bg-green-400 rounded-full"></div>
              <div className="h-3 w-3 bg-green-400 rounded-full"></div>
              <div className="h-3 w-3 bg-green-400 rounded-full"></div>
            </div>
          </div>
        )}

        {error && (
          <div className="text-center py-10">
            <p className="text-red-400">{error}</p>
          </div>
        )}

        {!loading && !error && (
          <div className="flex flex-wrap -mx-4">
            {calls.map((token, index) => (
              <motion.div
                key={token.id}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                viewport={{ once: true }}
                className="w-full sm:w-[calc(50%-1rem)] lg:w-[calc(33.333%-1rem)] mb-6 px-2"
              >
                <FeedCard token={token} />
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </section>
  )
}

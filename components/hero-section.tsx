"use client"

import { motion } from "framer-motion"
import Link from "next/link"

interface HeroSectionProps {
  title?: string
  subtitle?: string
  ctaText?: string
  ctaLink?: string
}

export default function HeroSection({
  title = "Live crypto calls.\nNo fluff. Just alpha.",
  subtitle = "Join the community of degens getting real-time signals and market insights before everyone else.",
  ctaText = "Join Telegram",
  ctaLink = "#",
}: HeroSectionProps) {
  // Split the title by newline to handle the formatting
  const titleParts = title.split("\n")

  return (
    <section className="relative py-20 md:py-32 overflow-hidden">
      {/* Background glow effect */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-pink-500/20 rounded-full blur-[100px] opacity-50"></div>

      <div className="container mx-auto px-4 relative z-10">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="text-center max-w-3xl mx-auto"
        >
          <h1 className="text-4xl md:text-6xl font-bold mb-6 leading-tight text-shadow-glow text-white">
            {titleParts[0]}
            {titleParts.length > 1 && (
              <>
                <br />
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-green-400 to-green-500">
                  {titleParts[1]}
                </span>
              </>
            )}
          </h1>

          <p className="text-lg md:text-xl text-white/80 mb-8 max-w-2xl mx-auto">{subtitle}</p>

          <Link href={ctaLink} className="inline-block">
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.98 }}
              className="px-8 py-3 rounded-lg bg-black/30 backdrop-blur-sm border border-green-400 text-white font-medium 
          shadow-[0_0_15px_rgba(91,255,51,0.5)] hover:shadow-[0_0_25px_rgba(91,255,51,0.8)] 
          transition-all duration-300"
            >
              {ctaText}
            </motion.button>
          </Link>
        </motion.div>
      </div>
    </section>
  )
}

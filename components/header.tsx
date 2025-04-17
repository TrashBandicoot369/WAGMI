"use client"

import { useState, useEffect } from "react"
import Link from "next/link"
import { Twitter, TextIcon as Telegram } from "lucide-react"

export default function Header() {
  const [scrolled, setScrolled] = useState(false)

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 10)
    }

    window.addEventListener("scroll", handleScroll)
    return () => window.removeEventListener("scroll", handleScroll)
  }, [])

  return (
    <header
      className={`sticky top-0 z-50 w-full transition-all duration-300 ${
        scrolled
          ? "bg-white/20 backdrop-blur-lg border-b border-green-500/20 shadow-lg shadow-green-500/10"
          : "bg-transparent"
      }`}
    >
      <div className="container mx-auto px-4 py-4 flex items-center justify-between">
        <div className="flex items-center">
          {/* Logo container with no background or borders */}
          <div className="h-40 w-auto flex items-center">
            {/* Position the logo to blend with the background */}
            <div className="absolute left-0 top-0 h-40 overflow-visible">
              <img src="/wagmi-logo.png" alt="WAGMI Logo" className="h-full object-contain object-left-top" />
            </div>
            {/* Spacer to maintain layout */}
            <div className="w-40 h-40"></div>
          </div>
        </div>

        <div className="hidden md:flex items-center space-x-6">
          <Link href="#" className="text-white hover:text-green-400 transition-colors font-medium">
            Home
          </Link>
          <Link href="#" className="text-white hover:text-green-400 transition-colors font-medium">
            Calls
          </Link>
          <Link href="#" className="text-white hover:text-green-400 transition-colors font-medium">
            About
          </Link>
          <div className="flex items-center space-x-4 ml-4">
            <Link href="#" className="text-white hover:text-green-400 transition-colors">
              <Twitter size={20} />
            </Link>
            <Link href="#" className="text-white hover:text-green-400 transition-colors">
              <Telegram size={20} />
            </Link>
          </div>
        </div>
      </div>
    </header>
  )
}

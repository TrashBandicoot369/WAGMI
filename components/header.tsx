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
      <div className="container mx-auto px-4 py-4 flex flex-col items-center">
        {/* Centered WAGMI logo at 3x size */}
        <div className="w-full flex justify-center mb-2">
          <img 
            src="/wagmi.png" 
            alt="WAGMI" 
            className="h-auto w-auto transform scale-300"
            style={{ maxWidth: '300px', transform: 'scale(3)', marginTop: '50px', marginBottom: '50px' }}
          />
        </div>
        
        {/* Navigation links below logo */}
        <div className="w-full flex justify-between items-center mt-16 pt-4">
          <div className="flex-1"></div> {/* Spacer */}
          
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
          
          <div className="flex-1"></div> {/* Spacer */}
        </div>
      </div>
    </header>
  )
}

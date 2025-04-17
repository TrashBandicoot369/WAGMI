"use client"

import { ExternalLink } from "lucide-react"
import Link from "next/link"
import { cn } from "@/lib/utils"

interface DexButtonProps {
  link: string
  className?: string
}

export function DexButton({ link, className }: DexButtonProps) {
  return (
    <Link
      href={link}
      target="_blank"
      rel="noopener noreferrer"
      className={cn(
        "flex items-center text-sm text-white/80 hover:text-green-400 transition-colors duration-200",
        className
      )}
    >
      <span className="mr-1">View on Dexscreener</span>
      <ExternalLink size={14} />
    </Link>
  )
} 
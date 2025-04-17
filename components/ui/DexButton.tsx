"use client"

import Link from "next/link"
import { cn } from "@/lib/utils"

interface DexButtonProps {
  link?: string;
  className?: string;
}

export function DexButton({ link, className }: DexButtonProps) {
  if (!link) {
    console.warn("⚠️ DexButton link missing!");
    return null;
  }

  return (
    <Link
      href={link}
      target="_blank"
      rel="noopener noreferrer"
      className={className}
    >
      View on Dexscreener
    </Link>
  );
} 
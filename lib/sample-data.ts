import type { TokenData } from "@/types"

// Sample data - this would be replaced with Firebase data in production
export const sampleTokenData: TokenData[] = [
  {
    id: "1",
    tokenName: "PEPE",
    timestamp: "Apr 17, 2025 - 4:20 PM",
    dexLink: "https://dexscreener.com/ethereum/pepe",
    isNew: true,
    status: "live",
  },
  {
    id: "2",
    tokenName: "WOJAK",
    timestamp: "Apr 17, 2025 - 3:15 PM",
    dexLink: "https://dexscreener.com/ethereum/wojak",
    isNew: true,
    status: "live",
  },
  {
    id: "3",
    tokenName: "DEGEN",
    timestamp: "Apr 17, 2025 - 2:30 PM",
    dexLink: "https://dexscreener.com/ethereum/degen",
    status: "live",
  },
  {
    id: "4",
    tokenName: "SHIB",
    timestamp: "Apr 17, 2025 - 1:45 PM",
    dexLink: "https://dexscreener.com/ethereum/shib",
    status: "completed",
  },
  {
    id: "5",
    tokenName: "FLOKI",
    timestamp: "Apr 17, 2025 - 12:30 PM",
    dexLink: "https://dexscreener.com/ethereum/floki",
    status: "completed",
  },
  {
    id: "6",
    tokenName: "BONK",
    timestamp: "Apr 17, 2025 - 11:15 AM",
    dexLink: "https://dexscreener.com/solana/bonk",
    status: "completed",
  },
]

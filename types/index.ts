// Define the token data interface
export interface TokenData {
  id: string
  token: string
  timestamp: any // or Date if you format on the fly
  status: "LIVE" | "COMPLETED" | "NEW"
  dexUrl: string
  isNew?: boolean
  
  // Market data
  marketCap?: number
  volume24h?: number
  initialMarketCap?: number
  athMarketCap?: number
  athGainPercent?: number
  percentChange24h?: number
  
  // Additional data seen in Firestore
  contract?: string
  capChange?: number
  lastRefreshed?: any
  updated?: any
  shotCaller?: boolean
  twitter?: string | null
  socials?: {
    twitter?: string
    website?: string
    [key: string]: any
  }
  
  // Additional optional fields
  groupName?: string
  confidence?: number
  chain?: string
}

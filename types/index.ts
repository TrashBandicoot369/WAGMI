// Define the token data interface
export interface TokenData {
  id: string
  token: string
  timestamp: any // or Date if you format on the fly
  status: "LIVE" | "COMPLETED" | "NEW"
  dexUrl: string
  isNew?: boolean
  groupName?: string
  confidence?: number
  chain?: string
}

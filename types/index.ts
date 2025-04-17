// Define the token data interface
export interface TokenData {
  id: string
  tokenName: string
  timestamp: string
  dexLink: string
  isNew?: boolean
  status?: "live" | "upcoming" | "completed"
}

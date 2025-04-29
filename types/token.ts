export interface TokenData {
  id: string;
  token: string;
  timestamp: number;
  dexUrl: string;
  isNew?: boolean;
  status?: string;
  marketCap?: number;
  initialMarketCap?: number;
  currentChange?: number;
  totalGainPercent?: number;
  volume24h?: number;
  contract?: string;
} 
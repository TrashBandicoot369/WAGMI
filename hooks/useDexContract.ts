"use client"

import { useState, useEffect } from 'react'

interface DexTokenInfo {
  contractAddress: string | null
  symbol: string | null
  error: string | null
  loading: boolean
}

/**
 * Hook to fetch token contract information from DexScreener
 * @param dexUrl The DexScreener URL for the token
 * @returns Object containing contract address, symbol, error state, and loading state
 */
export function useDexContract(dexUrl: string): DexTokenInfo {
  const [tokenInfo, setTokenInfo] = useState<DexTokenInfo>({
    contractAddress: null,
    symbol: null,
    error: null,
    loading: true
  })

  useEffect(() => {
    if (!dexUrl) {
      setTokenInfo({
        contractAddress: null,
        symbol: null,
        error: "No URL provided",
        loading: false
      })
      return
    }

    // Extract potential contract address or identifier from URL
    const urlParts = dexUrl.split('/')
    if (urlParts.length < 4) {
      setTokenInfo({
        contractAddress: null,
        symbol: null,
        error: "Invalid DexScreener URL format",
        loading: false
      })
      return
    }

    const chain = urlParts[urlParts.length - 2]
    const identifier = urlParts[urlParts.length - 1]

    // If the identifier looks like a contract address, use it directly
    if (identifier.length > 30 || identifier.startsWith('0x')) {
      setTokenInfo({
        contractAddress: identifier,
        symbol: null,
        error: null,
        loading: false
      })
      return
    }

    // Otherwise, fetch from DexScreener API
    const fetchContractAddress = async () => {
      try {
        // Using search endpoint to find by token name/symbol
        const response = await fetch(`https://api.dexscreener.com/latest/dex/search?q=${identifier}`)
        
        if (!response.ok) {
          throw new Error(`API responded with status: ${response.status}`)
        }
        
        const data = await response.json()
        
        if (data.pairs && data.pairs.length > 0) {
          // Find a pair that matches our chain if possible
          const pair = data.pairs.find((p: any) => 
            p.chainId.toLowerCase() === chain.toLowerCase()
          ) || data.pairs[0]
          
          setTokenInfo({
            contractAddress: pair.baseToken?.address || null,
            symbol: pair.baseToken?.symbol || null,
            error: null,
            loading: false
          })
        } else {
          setTokenInfo({
            contractAddress: identifier, // Fall back to the identifier from URL
            symbol: null,
            error: "No token data found",
            loading: false
          })
        }
      } catch (err) {
        console.error("Error fetching token data:", err)
        setTokenInfo({
          contractAddress: identifier, // Fall back to the identifier from URL
          symbol: null,
          error: err instanceof Error ? err.message : "Unknown error",
          loading: false
        })
      }
    }

    fetchContractAddress()
  }, [dexUrl])

  return tokenInfo
} 
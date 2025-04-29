#!/usr/bin/env python3

try:
    import requests
    import json
    from datetime import datetime
    import math
    import time
except ImportError:
    print("Error: The 'requests' package is not installed.")
    print("Please install it using:")
    print("pip install requests")
    exit(1)

def analyze_token():
    """Analyze UFD token data from DexScreener API"""
    print("\n🔍 Analyzing UFD Token")
    print("=" * 80)
    
    address = "eL5fUxj2J4CiQsmW85k5FG9DvuQjjUoBHoQBi2Kpump"
    tokens_url = f"https://api.dexscreener.com/latest/dex/tokens/{address}"
    
    try:
        response = requests.get(tokens_url)
        response.raise_for_status()
        result = response.json()
        
        if "pairs" in result and result["pairs"]:
            pair = result["pairs"][0]
            
            print("\n📊 Basic Token Information:")
            print("-" * 80)
            print(f"Name: {pair['baseToken']['name']}")
            print(f"Symbol: {pair['baseToken']['symbol']}")
            print(f"DEX: {pair['dexId']}")
            print(f"Price USD: ${float(pair['priceUsd']):.8f}")
            print(f"24h Volume: ${float(pair['volume']['h24']):,.2f}")
            
            txns = pair['txns']['h24']
            print("\n🔄 Trading Activity (24h):")
            print("-" * 80)
            print(f"Buys: {txns['buys']}")
            print(f"Sells: {txns['sells']}")
            
            changes = pair['priceChange']
            print("\n📈 Price Changes:")
            print("-" * 80)
            print(f"5m: {changes['m5']}%")
            print(f"1h: {changes['h1']}%")
            print(f"24h: {changes['h24']}%")
            
        else:
            print("No pairs found")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    analyze_token() 
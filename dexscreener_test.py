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

# Token addresses to test
TOKENS = {
    "UFD": "eL5fUxj2J4CiQsmW85k5FG9DvuQjjUoBHoQBi2Kpump",
    "WRITER": "HHxfxnQ7NEisim2DhkTx5Z65YAfnShjE52eobay9pump",
    "BONK": "5DBCneKX6HtZezFfMPqWy6UiK4xhsrm3HZX57cbT3sVe",
    "PUMP1": "FJtAheX8Hcz2BMqwizf6GBwghbBgtvPUnEpC9Azipump",
    "PUMP2": "DhDzK4deAoU9K5pmzqXiFH9WPEynAiyWAcLEZp8pump",
    "PUMP3": "69aXy2NVWbpqbAhDb71CcWGJEu9PXnPMfpsPVGumpump"
}

def get_pair_data(pair_address):
    """Get detailed pair data using DexScreener pairs API"""
    url = f"https://api.dexscreener.com/latest/dex/pairs/solana/{pair_address}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        result = response.json()
        return result.get('pair', {})
    except Exception as e:
        print(f"Warning: Could not fetch pair data: {str(e)}")
        return {}

def format_value(value, value_type="string"):
    """Format values with availability indicator"""
    if value_type == "price":
        return f"${float(value):,.8f}" if value else "N/A"
    elif value_type == "number":
        return f"{float(value):,.2f}" if value else "N/A"
    elif value_type == "currency":
        if not value:
            return "N/A"
        value = float(value)
        if value >= 1_000_000:
            return f"${value/1_000_000:.2f}M"
        elif value >= 1_000:
            return f"${value/1_000:.2f}K"
        else:
            return f"${value:.2f}"
    else:
        return str(value) if value else "N/A"

def analyze_token(symbol, address):
    """Analyze token data from both APIs and show data availability"""
    print(f"\n🔍 Analyzing {symbol}: {address}")
    print("=" * 80)
    
    # Get data from tokens API
    tokens_url = f"https://api.dexscreener.com/latest/dex/tokens/{address}"
    tokens_data = {}
    pairs_data = {}
    
    try:
        response = requests.get(tokens_url)
        response.raise_for_status()
        result = response.json()
        if "pairs" in result and result["pairs"]:
            tokens_data = result["pairs"][0]
            
            # Get data from pairs API
            pair_address = tokens_data.get('pairAddress')
            if pair_address:
                pairs_data = get_pair_data(pair_address)
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return

    # Basic Token Info
    print("\n📊 Basic Token Information:")
    print("-" * 80)
    print(f"{'Field':<30} {'Tokens API':<25} {'Pairs API':<25}")
    print("-" * 80)
    print(f"{'Name':<30} {tokens_data.get('baseToken', {}).get('name', 'N/A'):<25} {pairs_data.get('baseToken', {}).get('name', 'N/A'):<25}")
    print(f"{'Symbol':<30} {tokens_data.get('baseToken', {}).get('symbol', 'N/A'):<25} {pairs_data.get('baseToken', {}).get('symbol', 'N/A'):<25}")
    print(f"{'DEX':<30} {tokens_data.get('dexId', 'N/A'):<25} {pairs_data.get('dexId', 'N/A'):<25}")

    # Price & Volume Data
    print("\n💰 Price & Volume Data:")
    print("-" * 80)
    print(f"{'Field':<30} {'Tokens API':<25} {'Pairs API':<25}")
    print("-" * 80)
    print(f"{'Price USD':<30} {format_value(tokens_data.get('priceUsd'), 'price'):<25} {format_value(pairs_data.get('priceUsd'), 'price'):<25}")
    print(f"{'24h Volume':<30} {format_value(tokens_data.get('volume', {}).get('h24'), 'currency'):<25} {format_value(pairs_data.get('volume', {}).get('h24'), 'currency'):<25}")
    
    # Price Changes
    print("\n📈 Price Changes:")
    print("-" * 80)
    print(f"{'Field':<30} {'Tokens API':<25} {'Pairs API':<25}")
    print("-" * 80)
    t_changes = tokens_data.get('priceChange', {})
    p_changes = pairs_data.get('priceChange', {})
    print(f"{'5m Change':<30} {format_value(t_changes.get('m5'), 'number')}%<25 {format_value(p_changes.get('m5'), 'number')}%<25")
    print(f"{'1h Change':<30} {format_value(t_changes.get('h1'), 'number')}%<25 {format_value(p_changes.get('h1'), 'number')}%<25")
    print(f"{'6h Change':<30} {format_value(t_changes.get('h6'), 'number')}%<25 {format_value(p_changes.get('h6'), 'number')}%<25")
    print(f"{'24h Change':<30} {format_value(t_changes.get('h24'), 'number')}%<25 {format_value(p_changes.get('h24'), 'number')}%<25")

    # Liquidity & Reserves
    print("\n💧 Liquidity & Reserves:")
    print("-" * 80)
    print(f"{'Field':<30} {'Tokens API':<25} {'Pairs API':<25}")
    print("-" * 80)
    t_liq = tokens_data.get('liquidity', {})
    p_liq = pairs_data.get('liquidity', {})
    print(f"{'Liquidity USD':<30} {format_value(t_liq.get('usd'), 'currency'):<25} {format_value(p_liq.get('usd'), 'currency'):<25}")
    print(f"{'Base Reserves':<30} {format_value(t_liq.get('base'), 'number'):<25} {format_value(p_liq.get('base'), 'number'):<25}")
    print(f"{'Quote Reserves':<30} {format_value(t_liq.get('quote'), 'number'):<25} {format_value(p_liq.get('quote'), 'number'):<25}")

    # Trading Activity
    print("\n🔄 Trading Activity (24h):")
    print("-" * 80)
    print(f"{'Field':<30} {'Tokens API':<25} {'Pairs API':<25}")
    print("-" * 80)
    t_txns = tokens_data.get('txns', {}).get('h24', {})
    p_txns = pairs_data.get('txns', {}).get('h24', {})
    print(f"{'Buys':<30} {format_value(t_txns.get('buys'), 'number'):<25} {format_value(p_txns.get('buys'), 'number'):<25}")
    print(f"{'Sells':<30} {format_value(t_txns.get('sells'), 'number'):<25} {format_value(p_txns.get('sells'), 'number'):<25}")

    # Additional Metrics
    print("\n📝 Additional Metrics:")
    print("-" * 80)
    print(f"{'Field':<30} {'Tokens API':<25} {'Pairs API':<25}")
    print("-" * 80)
    print(f"{'Price Since Launch':<30} {format_value(t_changes.get('sinceLaunch'), 'number')}%<25 {format_value(p_changes.get('sinceLaunch'), 'number')}%<25")
    print(f"{'ATH Price':<30} {format_value(tokens_data.get('athPrice'), 'price'):<25} {format_value(pairs_data.get('athPrice'), 'price'):<25}")
    print(f"{'ATL Price':<30} {format_value(tokens_data.get('atlPrice'), 'price'):<25} {format_value(pairs_data.get('atlPrice'), 'price'):<25}")

def main():
    print("🔄 Analyzing data availability from both DexScreener APIs...")
    for symbol, address in TOKENS.items():
        analyze_token(symbol, address)
        time.sleep(1)  # Add small delay between requests

if __name__ == "__main__":
    main() 
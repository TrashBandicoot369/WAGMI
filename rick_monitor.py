#!/usr/bin/env python3

try:
    import requests
    import json
    from datetime import datetime
    import math
    import time
    import sys
except ImportError:
    print("Error: Required packages are not installed.")
    print("Please install them using:")
    print("pip install requests")
    exit(1)

import os
import re
import asyncio
import logging
import signal
import aiohttp
from aiohttp import web

import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from telethon import TelegramClient, events
from firebase_admin_setup import db
from firebase_admin import firestore

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='\n%(asctime)s\n%(levelname)s: %(message)s\n',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.StreamHandler(stream=sys.stdout),
        logging.FileHandler('rick_monitor.log', encoding='utf-8')
    ]
)
logger = logging.getLogger("rick_monitor")

# Config
API_ID = 26108909
API_HASH = "3cb55b9919cee50e576611641283ec5a"
SOURCE_GROUPS = [-1002416386782]

START_TIME = time.time()
is_shutting_down = False
health_status = "STARTING"

telegram_semaphore = asyncio.Semaphore(1)
firestore_semaphore = asyncio.Semaphore(5)

def fetch_token_data(contract_address):
    """Fetch token data from DexScreener API"""
    url = f"https://api.dexscreener.com/latest/dex/tokens/{contract_address}"
    try:
        response = requests.get(url)
        if response.status_code != 200:
            print(f"DexScreener API error {response.status_code}: {response.text}")
            return None
        
        data = response.json()
        if not data.get("pairs"):
            print(f"No pairs found for {contract_address}")
            return None
            
        # Get the most liquid pair
        pair = data["pairs"][0]
        
        # Extract consistently available data
        token_data = {
            "chain": "solana",
            "contract": contract_address,
            "symbol": pair.get("baseToken", {}).get("symbol", ""),
            "name": pair.get("baseToken", {}).get("name", ""),
            "priceUsd": float(pair.get("priceUsd", 0)),
            "volume24h": float(pair.get("volume", {}).get("h24", 0)),
            "dexId": pair.get("dexId", ""),
            "dexUrl": pair.get("url", f"https://dexscreener.com/solana/{contract_address}"),
            "pairAddress": pair.get("pairAddress", ""),
            "timestamp": firestore.SERVER_TIMESTAMP,
            "updated": firestore.SERVER_TIMESTAMP,
            "status": "LIVE"
        }
        
        # Add trading metrics
        txns = pair.get("txns", {}).get("h24", {})
        token_data.update({
            "buys24h": int(txns.get("buys", 0)),
            "sells24h": int(txns.get("sells", 0))
        })
        
        # Add price changes
        price_changes = pair.get("priceChange", {})
        token_data.update({
            "priceChange": {
                "m5": float(price_changes.get("m5", 0)),
                "h1": float(price_changes.get("h1", 0)),
                "h6": float(price_changes.get("h6", 0)),
                "h24": float(price_changes.get("h24", 0))
            }
        })
        
        return token_data
    except Exception as e:
        print(f"Token data fetch failed: {e}")
        return None

class TokenParser:
    @staticmethod
    def parse_number(value_str):
        try:
            if not value_str:
                return 0
            value_str = value_str.replace('$', '').strip()
            multipliers = {'K': 1000, 'M': 1000000, 'B': 1000000000}
            suffix = value_str[-1].upper()
            if suffix in multipliers:
                number = float(value_str[:-1])
                return number * multipliers[suffix]
            return float(value_str)
        except:
            return 0

    @staticmethod
    def parse_message(message_text):
        try:
            contract_match = re.search(r'`([1-9A-HJ-NP-Za-km-z]{32,44})`', message_text)
            symbol_match = re.search(r'\*\*\$([A-Z0-9]+)\*\*', message_text)
            
            if not contract_match or not symbol_match:
                return None

            # Get initial data from message
            initial_data = {
                "chain": "solana",
                "contract": contract_match.group(1),
                "symbol": symbol_match.group(1),
                "status": "LIVE",
                "timestamp": firestore.SERVER_TIMESTAMP,
                "updated": firestore.SERVER_TIMESTAMP
            }
            
            # Fetch real-time data from DexScreener
            dex_data = fetch_token_data(initial_data["contract"])
            if dex_data:
                initial_data.update(dex_data)
            
            return initial_data
        except Exception as e:
            logger.error(f"Message parsing failed: {e}")
            return None

async def firestore_updater():
    while True:
        try:
            logger.info("🔄 Updating token data from DexScreener...")
            tokens = db.collection('calls').stream()
            for doc in tokens:
                data = doc.to_dict()
                contract = data.get("contract")

                if not contract or len(contract) < 32:
                    logger.warning(f"Invalid contract: {contract}")
                    continue

                token_data = fetch_token_data(contract)
                if token_data:
                    # Update only market data fields, preserving initialMarketCap
                    update_data = {
                        "priceUsd": token_data["priceUsd"],
                        "volume24h": token_data["volume24h"],
                        "marketCap": token_data.get("marketCap", 0),
                        "priceChange": token_data["priceChange"],
                        "buys24h": token_data["buys24h"],
                        "sells24h": token_data["sells24h"],
                        "updated": firestore.SERVER_TIMESTAMP,
                        "lastRefreshed": firestore.SERVER_TIMESTAMP
                    }

                    # Update ATH if current market cap is higher
                    current_ath = data.get("athMarketCap", 0)
                    if token_data.get("marketCap", 0) > current_ath:
                        update_data["athMarketCap"] = token_data.get("marketCap", 0)

                    db.collection('calls').document(doc.id).update(update_data)
                    logger.info(f"✅ Updated {data.get('symbol')} | Price: ${token_data['priceUsd']:.8f} | Vol: ${token_data['volume24h']:,.2f}")
            logger.info("✅ Token update cycle complete.")
        except Exception as e:
            logger.error(f"Updater error: {e}")
        await asyncio.sleep(300)  # 5 minutes

async def health_check_server():
    app = web.Application()
    async def handle_health(request):
        client_ok = monitor.client.is_connected() if 'monitor' in globals() else False
        return web.json_response({"status": health_status}, status=200 if client_ok else 500)
    app.router.add_get('/health', handle_health)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8081)
    await site.start()

class TelegramMonitor:
    def __init__(self):
        self.client = TelegramClient("user_session2", API_ID, API_HASH)

    async def message_handler(self, event):
        sender = await event.get_sender()
        if sender.username != "RickBurpBot":
            return
        token_data = TokenParser.parse_message(event.message.text)
        if not token_data:
            return
        docs = db.collection('calls').where('contract', '==', token_data['contract']).limit(1).get()
        if not list(docs):
            db.collection('calls').add(token_data)

def test_ufd():
    """Test function to check UFD token data fetching"""
    print("\n🔍 Analyzing UFD Token")
    print("=" * 80)
    
    address = "eL5fUxj2J4CiQsmW85k5FG9DvuQjjUoBHoQBi2Kpump"
    
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
                pairs_url = f"https://api.dexscreener.com/latest/dex/pairs/solana/{pair_address}"
                pair_response = requests.get(pairs_url)
                pair_response.raise_for_status()
                pairs_data = pair_response.json().get('pair', {})
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return

    # Basic Token Info
    print("\n📊 Basic Token Information:")
    print("-" * 80)
    print(f"Name: {tokens_data.get('baseToken', {}).get('name', 'N/A')}")
    print(f"Symbol: {tokens_data.get('baseToken', {}).get('symbol', 'N/A')}")
    print(f"DEX: {tokens_data.get('dexId', 'N/A')}")

    # Price & Volume Data
    print("\n💰 Price & Volume Data:")
    print("-" * 80)
    print(f"Price USD: ${float(tokens_data.get('priceUsd', 0)):.8f}")
    print(f"24h Volume: ${float(tokens_data.get('volume', {}).get('h24', 0)):,.2f}")
    
    # Trading Activity
    txns = tokens_data.get('txns', {}).get('h24', {})
    print("\n🔄 Trading Activity (24h):")
    print("-" * 80)
    print(f"Buys: {txns.get('buys', 'N/A')}")
    print(f"Sells: {txns.get('sells', 'N/A')}")

    # Price Changes
    changes = tokens_data.get('priceChange', {})
    print("\n📈 Price Changes:")
    print("-" * 80)
    print(f"5m: {changes.get('m5', 'N/A')}%")
    print(f"1h: {changes.get('h1', 'N/A')}%")
    print(f"24h: {changes.get('h24', 'N/A')}%")

def main():
    """Main function"""
    try:
        test_ufd()
        print("\nTest completed. Press Ctrl+C to exit.")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nTest terminated by user")
        sys.exit(0)

if __name__ == "__main__":
    main()

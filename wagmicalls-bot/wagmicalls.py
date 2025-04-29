#!/usr/bin/env python3

import requests
import json
import logging
from datetime import datetime
import time
from typing import Dict, Optional, Any, List
import firebase_admin
from firebase_admin import credentials, firestore
import re
import asyncio
import signal
from telethon import TelegramClient, events
import sys
import threading

# Configure logging with millisecond precision
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03d - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.StreamHandler(stream=sys.stdout),
        logging.FileHandler('wagmi_calls_detailed.log', encoding='utf-8')
    ]
)
logger = logging.getLogger("wagmi_calls")

# Telegram Config
API_ID = 26108909
API_HASH = "3cb55b9919cee50e576611641283ec5a"
SOURCE_GROUPS = [-1002416386782]  # Group to monitor
is_shutting_down = False

# Add operation timing logging
def log_operation_time(operation_name):
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            logger.info(f"🕒 Starting {operation_name}")
            try:
                result = await func(*args, **kwargs)
                elapsed = (time.time() - start_time) * 1000
                logger.info(f"✅ Completed {operation_name} in {elapsed:.2f}ms")
                return result
            except Exception as e:
                elapsed = (time.time() - start_time) * 1000
                logger.error(f"❌ Failed {operation_name} after {elapsed:.2f}ms: {str(e)}")
                raise
        
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            logger.info(f"🕒 Starting {operation_name}")
            try:
                result = func(*args, **kwargs)
                elapsed = (time.time() - start_time) * 1000
                logger.info(f"✅ Completed {operation_name} in {elapsed:.2f}ms")
                return result
            except Exception as e:
                elapsed = (time.time() - start_time) * 1000
                logger.error(f"❌ Failed {operation_name} after {elapsed:.2f}ms: {str(e)}")
                raise
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator

class TelegramMonitor:
    """Class to handle Telegram monitoring"""
    
    def __init__(self, api: 'DexScreenerAPI', firebase: 'FirebaseManager'):
        self.client = TelegramClient("user_session2", API_ID, API_HASH)
        self.api = api
        self.firebase = firebase
        
    async def start(self):
        """Start the Telegram client and add message handler"""
        await self.client.start()
        logger.info("✅ Telegram client connected")
        
        # Add message handler
        @self.client.on(events.NewMessage(chats=SOURCE_GROUPS))
        async def message_handler(event):
            try:
                # Check if message is from RickBurpBot
                sender = await event.get_sender()
                if sender.username != "RickBurpBot":
                    return
                    
                # Parse contract address from message
                contract_match = re.search(r'`([1-9A-HJ-NP-Za-km-z]{32,44})`', event.message.text)
                if not contract_match:
                    return
                    
                contract = contract_match.group(1)
                logger.info(f"🔍 Found contract in RickBurpBot message: {contract}")
                
                # Get token data
                token_data = self.api.get_token_data(contract)
                if token_data:
                    # Store in Firebase
                    if self.firebase.store_token_data(token_data):
                        logger.info(f"✅ Processed and stored data for {token_data['symbol']}")
                    else:
                        logger.error(f"❌ Failed to store data for contract {contract}")
                else:
                    logger.error(f"❌ Failed to fetch data for contract {contract}")
                    
            except Exception as e:
                logger.error(f"❌ Error processing message: {e}")
        
        logger.info(f"🔄 Now monitoring group {SOURCE_GROUPS[0]} for RickBurpBot messages")
        
    async def run(self):
        """Run the client until disconnected"""
        await self.client.run_until_disconnected()
        
    def stop(self):
        """Stop the client"""
        self.client.disconnect()
        logger.info("👋 Telegram client disconnected")

class FirebaseManager:
    """Class to handle Firebase operations"""
    
    def __init__(self):
        try:
            # Initialize Firebase if not already initialized
            if not firebase_admin._apps:
                cred = credentials.Certificate("wagmi-crypto-calls-firebase-adminsdk-fbsvc-88527b62f1.json")
                firebase_admin.initialize_app(cred)
            self.db = firestore.client()
            logger.info("✅ Firebase initialized successfully")
        except Exception as e:
            logger.error(f"❌ Firebase initialization error: {e}")
            raise e
    
    @log_operation_time("Firestore Get All Tokens")
    def get_all_tokens(self) -> List[Dict]:
        """Get all tokens from Firestore"""
        try:
            docs = self.db.collection('calls').get()
            tokens = [doc.to_dict() for doc in docs]
            logger.info(f"📊 Retrieved {len(tokens)} tokens from Firestore")
            return tokens
        except Exception as e:
            logger.error(f"❌ Failed to get tokens: {e}")
            return []
    
    @log_operation_time("Firestore Store Token")
    def store_token_data(self, token_data: Dict) -> bool:
        """
        Store token data in Firestore
        Returns True if successful, False otherwise
        """
        try:
            # Log the operation start
            logger.info(f"💾 Storing data for token {token_data.get('symbol', 'Unknown')}")
            
            # Check if document already exists
            docs = self.db.collection('calls').where('contract', '==', token_data['contract']).limit(1).get()
            existing_docs = list(docs)
            
            if existing_docs:
                doc = existing_docs[0]
                doc_data = doc.to_dict()
                
                # Log the update operation
                logger.info(f"🔄 Updating existing token: {token_data.get('symbol')} - Current MC: ${token_data.get('marketCap', 0):,.2f}")
                
                # Keep the original initial market cap, never update it
                initial_mc = doc_data.get('initialMarketCap')
                if initial_mc:
                    token_data['initialMarketCap'] = initial_mc
                    # Calculate total gain from initial to current
                    if token_data['marketCap']:
                        token_data['totalGainPercent'] = ((token_data['marketCap'] - initial_mc) / initial_mc) * 100
                        logger.info(f"📈 Total gain for {token_data['symbol']}: {token_data['totalGainPercent']:.2f}%")
                
                # Log the update details
                logger.info(f"📝 Update details for {token_data['symbol']}:")
                logger.info(f"   - Market Cap: ${token_data.get('marketCap', 0):,.2f}")
                logger.info(f"   - Initial MC: ${token_data.get('initialMarketCap', 0):,.2f}")
                logger.info(f"   - Volume 24h: ${token_data.get('volume24h', 0):,.2f}")
                
                doc.reference.update({
                    "marketCap": token_data["marketCap"],
                    "currentChange": token_data["currentChange"],
                    "totalGainPercent": token_data.get("totalGainPercent"),
                    "volume24h": token_data["volume24h"],
                    "buys24h": token_data["buys24h"],
                    "sells24h": token_data["sells24h"],
                    "updated": firestore.SERVER_TIMESTAMP
                })
                logger.info(f"✅ Successfully updated {token_data['symbol']}")
            else:
                # Log new token creation
                logger.info(f"➕ Creating new token entry: {token_data.get('symbol')}")
                token_data['initialMarketCap'] = token_data['marketCap']
                token_data['totalGainPercent'] = 0
                token_data['timestamp'] = firestore.SERVER_TIMESTAMP
                token_data['updated'] = firestore.SERVER_TIMESTAMP
                self.db.collection('calls').add(token_data)
                logger.info(f"✅ Successfully created new entry for {token_data['symbol']}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to store token data: {e}")
            if hasattr(e, '__traceback__'):
                logger.error(f"Traceback: {e.__traceback__.tb_frame.f_code.co_filename}:{e.__traceback__.tb_lineno}")
            return False

class DexScreenerAPI:
    """Class to handle DexScreener API interactions"""
    
    def __init__(self):
        self.base_url = "https://api.dexscreener.com/latest/dex"
        self.rate_limit_delay = 1.0  # 1 second between requests
        self.batch_size = 10  # Process 10 tokens at a time
        
    def format_value(self, value: Any, value_type: str = "string") -> str:
        """Format values with proper formatting based on type"""
        if value is None:
            return "N/A"
            
        if value_type == "price":
            return f"${float(value):,.8f}"
        elif value_type == "number":
            return f"{float(value):,.2f}"
        elif value_type == "currency":
            value = float(value)
            if value >= 1_000_000_000:
                return f"${value/1_000_000_000:.2f}B"
            elif value >= 1_000_000:
                return f"${value/1_000_000:.2f}M"
            elif value >= 1_000:
                return f"${value/1_000:.2f}K"
            else:
                return f"${value:.2f}"
        else:
            return str(value)

    async def refresh_tokens(self, firebase_manager: 'FirebaseManager'):
        """Refresh all token data every 5 minutes"""
        while not is_shutting_down:
            try:
                # Get all tokens from Firebase
                tokens = firebase_manager.get_all_tokens()
                logger.info(f"🔄 Starting refresh for {len(tokens)} tokens")
                
                # Process tokens in batches
                for i in range(0, len(tokens), self.batch_size):
                    batch = tokens[i:i + self.batch_size]
                    
                    for token in batch:
                        if is_shutting_down:
                            return
                            
                        try:
                            # Get updated data
                            updated_data = self.get_token_data(token['contract'])
                            if updated_data:
                                firebase_manager.store_token_data(updated_data)
                                logger.info(f"✅ Refreshed data for {updated_data['symbol']}")
                            else:
                                logger.warning(f"⚠️ Failed to refresh data for {token['contract']}")
                                
                            # Rate limiting delay
                            await asyncio.sleep(self.rate_limit_delay)
                            
                        except Exception as e:
                            logger.error(f"❌ Error refreshing token {token['contract']}: {e}")
                            continue
                    
                    # Add a small delay between batches
                    await asyncio.sleep(2)
                
                logger.info("✅ Completed token refresh cycle")
                
                # Wait for 5 minutes before next refresh
                await asyncio.sleep(300)  # 5 minutes
                
            except Exception as e:
                logger.error(f"❌ Error in refresh cycle: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error before retrying

    @log_operation_time("DexScreener API Call")
    def get_token_data(self, contract_address: str) -> Optional[Dict]:
        """
        Fetch token data from DexScreener API
        Returns None if the request fails or no data is found
        """
        url = f"{self.base_url}/tokens/{contract_address}"
        
        try:
            logger.info(f"🔍 Fetching data for contract: {contract_address}")
            start_time = time.time()
            
            response = requests.get(url)
            response.raise_for_status()
            
            api_time = (time.time() - start_time) * 1000
            logger.info(f"⏱️ DexScreener API response time: {api_time:.2f}ms")
            
            data = response.json()
            if not data.get("pairs"):
                logger.warning(f"⚠️ No pairs found for {contract_address}")
                return None
                
            # Get the most liquid pair
            pair = data["pairs"][0]
            
            # Extract data and log
            token_data = {
                "chain": "solana",
                "contract": contract_address,
                "symbol": pair.get("baseToken", {}).get("symbol", ""),
                "name": pair.get("baseToken", {}).get("name", ""),
                "marketCap": float(pair.get("marketCap", 0)),
                "currentChange": float(pair.get("priceChange", {}).get("h24", 0)),
                "volume24h": float(pair.get("volume", {}).get("h24", 0)),
                "dexId": pair.get("dexId", ""),
                "dexUrl": pair.get("url", f"https://dexscreener.com/solana/{contract_address}"),
                "pairAddress": pair.get("pairAddress", ""),
                "status": "LIVE"
            }
            
            # Add trading metrics
            txns = pair.get("txns", {}).get("h24", {})
            token_data.update({
                "buys24h": int(txns.get("buys", 0)),
                "sells24h": int(txns.get("sells", 0))
            })
            
            logger.info(f"✅ Successfully fetched data for {token_data['symbol']}")
            return token_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ API request failed: {e}")
            return None
        except (KeyError, ValueError, TypeError) as e:
            logger.error(f"❌ Data parsing failed: {e}")
            return None
            
    def print_token_analysis(self, token_data: Dict):
        """Print a formatted analysis of token data"""
        if not token_data:
            logger.error("No token data to analyze")
            return
            
        print("\n" + "="*80)
        print(f"🔍 Token Analysis: {token_data['symbol']}")
        print("="*80)
        
        # Basic Info
        print("\n📊 Basic Information:")
        print(f"Name: {token_data['name']}")
        print(f"Symbol: {token_data['symbol']}")
        print(f"Contract: {token_data['contract']}")
        print(f"DEX: {token_data['dexId']}")
        
        # Market Data
        print("\n💰 Market Data:")
        print(f"Market Cap: {self.format_value(token_data['marketCap'], 'currency')} ({self.format_value(token_data['currentChange'], 'number')}%)")
        print(f"Initial Market Cap: {self.format_value(token_data['initialMarketCap'], 'currency')} (Highest: {self.format_value(token_data['highestChange'], 'number')}%)")
        print(f"24h Volume: {self.format_value(token_data['volume24h'], 'currency')}")
        
        # Trading Activity
        print("\n🔄 Trading Activity (24h):")
        print(f"Buys: {token_data['buys24h']}")
        print(f"Sells: {token_data['sells24h']}")
        
        print("\n" + "="*80)

async def main():
    """Main function to run the monitoring service"""
    try:
        # Initialize services
        api = DexScreenerAPI()
        firebase = FirebaseManager()
        monitor = TelegramMonitor(api, firebase)
        
        # Setup signal handlers
        def signal_handler(sig, frame):
            logger.info("🛑 Received shutdown signal, stopping gracefully...")
            global is_shutting_down
            is_shutting_down = True
            monitor.stop()
            sys.exit(0)
            
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Start monitoring and refreshing
        logger.info("🚀 Starting WAGMI Calls monitoring service...")
        
        # Create tasks for both monitoring and refreshing
        monitor_task = asyncio.create_task(monitor.start())
        refresh_task = asyncio.create_task(api.refresh_tokens(firebase))
        
        # Run both tasks concurrently
        await asyncio.gather(monitor_task, refresh_task)
        await monitor.run()
        
    except Exception as e:
        logger.error(f"❌ Critical error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 
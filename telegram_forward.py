import asyncio
from telethon.sync import TelegramClient
from telethon.tl.types import PeerChannel
from lib.firebase_admin_setup import db
import os
from google.cloud import firestore

# Telegram API Config
API_ID = 29312830
API_HASH = "24622c388a689db6cf871903fdca8c1c"
# We'll use client mode instead of bot mode for testing
USE_BOT = False
BOT_TOKEN = None  # Not needed for client mode test

# Target Telegram Chat IDs - using IDs where we have posting permission
CHAT_IDS = [
    2416386782,  # ShotCollaz
    2433374813,  # Really Good Business Ethics
    2651955296   # WAGMI
]

# Session file must exist in your project root
SESSION_FILE = 'user_session2'  # Using a different session file to avoid locking issues

async def send_message_to_telegram(client, chat_id, message):
    """Send a message to a Telegram chat/channel"""
    try:
        # Using markdown parse mode for formatting
        await client.send_message(chat_id, message, parse_mode='md')
        print(f"✅ Message sent to chat {chat_id}")
        return True
    except Exception as e:
        print(f"❌ Error sending message to {chat_id}: {e}")
        return False

async def format_call_message(call_data):
    """Format a call data into a Telegram message"""
    symbol = call_data.get('symbol', call_data.get('token', 'UNKNOWN'))
    market_cap = call_data.get('marketCap', 0)
    volume = call_data.get('volume24h', 0)
    dex_url = call_data.get('dexUrl', '')
    
    # Format market cap and volume with K/M/B suffixes
    def format_number(num):
        if num >= 1_000_000_000:
            return f"{num / 1_000_000_000:.1f}B"
        elif num >= 1_000_000:
            return f"{num / 1_000_000:.1f}M"
        elif num >= 1_000:
            return f"{num / 1_000:.1f}K"
        else:
            return str(num)
    
    # Create message
    message = f"🚨 **NEW CALL** 🚨\n\n"
    message += f"**${symbol}**\n\n"
    
    if market_cap:
        message += f"💰 Market Cap: **${format_number(market_cap)}**\n"
    
    if volume:
        message += f"📊 Volume (24h): **${format_number(volume)}**\n"
    
    if dex_url:
        message += f"\n🔍 [View on DEX]({dex_url})\n"
    
    message += "\n*This is a test message*"
    
    return message

async def create_test_call():
    """Create a test call in Firestore and return its ID"""
    test_call = {
        "symbol": "TEST",
        "token": "TEST",
        "dexUrl": "https://dexscreener.com/solana/GN2G7d2qWfsfG3j6CXsiHuuTN5Huzkq4dq86Y4o7yiKc",
        "contract": "GN2G7d2qWfsfG3j6CXsiHuuTN5Huzkq4dq86Y4o7yiKc",
        "timestamp": firestore.SERVER_TIMESTAMP,
        "status": "LIVE",
        "marketCap": 100000,
        "volume24h": 50000,
        "initialMarketCap": 80000,
        "athMarketCap": 150000,
        "percentChange24h": 25.5,
        "isNew": True,
        "chain": "solana",
        "shotCaller": False,
        "forwarded": False
    }
    
    # Add to Firestore
    doc_ref = db.collection("calls").add(test_call)
    print("✅ Test call created for forwarding")
    return doc_ref[1].id

async def test_telegram_forwarding():
    """Create a test call and forward it to Telegram"""
    print("🧪 Running Telegram forwarding test...")
    
    # Create a test call first
    try:
        call_id = await create_test_call()
        
        # Get the call data
        call_doc = db.collection("calls").document(call_id).get()
        call_data = call_doc.to_dict()
        
        # Format the message
        message = await format_call_message(call_data)
        print("📝 Formatted test message:")
        print(message)
    except Exception as e:
        print(f"❌ Error creating test call: {e}")
        return
    
    # Start Telegram client
    client = None
    try:
        client = TelegramClient(SESSION_FILE, API_ID, API_HASH)
        await client.start()
        print("✅ Connected to Telegram using existing session")
        
        # Make sure we're properly connected
        me = await client.get_me()
        print(f"✅ Authenticated as: {me.username or me.phone}")
        
        # Try sending to each chat
        for chat_id in CHAT_IDS:
            print(f"📤 Attempting to send to chat {chat_id}...")
            success = await send_message_to_telegram(client, chat_id, message)
            
            if success:
                print(f"✅ Successfully sent test message to {chat_id}")
                # Mark as forwarded
                db.collection("calls").document(call_id).update({"forwarded": True})
            else:
                print(f"❌ Failed to send test message to {chat_id}")
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
    
    finally:
        # Disconnect client
        if client:
            try:
                await client.disconnect()
                print("👋 Disconnected from Telegram")
            except Exception as e:
                print(f"⚠️ Error disconnecting: {e}")

if __name__ == "__main__":
    asyncio.run(test_telegram_forwarding()) 
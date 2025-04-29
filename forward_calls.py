import asyncio
from telethon.sync import TelegramClient
from lib.firebase_admin_setup import db
from google.cloud import firestore
import os
import time
import sys

# Telegram API Config
API_ID = 29312830
API_HASH = "24622c388a689db6cf871903fdca8c1c"

# Target Telegram Chat IDs - using IDs where we have posting permission
CHAT_IDS = [
    2416386782,  # ShotCollaz
    2433374813,  # Really Good Business Ethics
    2651955296   # WAGMI
]

# Session file must exist in your project root
SESSION_FILE = 'forward_session'  # Using a dedicated session file for forwarding

async def send_message_to_telegram(client, chat_id, message):
    """Send a message to a Telegram chat/channel"""
    try:
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
    
    if call_data.get('athMarketCap'):
        ath = call_data.get('athMarketCap')
        message += f"🏆 ATH Market Cap: **${format_number(ath)}**\n"
    
    # Include percent change if available
    if call_data.get('percentChange24h'):
        pct = call_data.get('percentChange24h')
        pct_symbol = "+" if pct > 0 else ""
        message += f"📈 24h Change: **{pct_symbol}{pct}%**\n"
    
    if dex_url:
        message += f"\n🔍 [View on DEX]({dex_url})\n"
    
    # Add Twitter link if available
    if call_data.get('twitter'):
        message += f"🐦 [Twitter]({call_data.get('twitter')})\n"
    
    return message

async def forward_new_calls():
    """Forward new calls from Firestore to Telegram channels"""
    print("🔄 Starting Telegram call forwarding...")
    
    # Start Telegram client
    client = None
    try:
        client = TelegramClient(SESSION_FILE, API_ID, API_HASH)
        await client.start()
        print("✅ Connected to Telegram")
        
        # Make sure we're properly connected
        me = await client.get_me()
        print(f"✅ Authenticated as: {me.username or me.phone}")
        
        # Get calls that haven't been forwarded
        calls_ref = db.collection("calls")
        
        # First try to find calls explicitly marked as not forwarded
        query1 = calls_ref.where("forwarded", "==", False).limit(10)
        calls = list(query1.stream())
        
        # If none found, look for calls without the forwarded field
        if not calls:
            print("No calls explicitly marked as not forwarded, checking for calls without forwarded field...")
            # This is a more complex query - we need to find documents where the field doesn't exist
            # Get recent calls and filter in memory
            query2 = calls_ref.order_by("timestamp", direction=firestore.Query.DESCENDING).limit(25)
            recent_calls = list(query2.stream())
            calls = [call for call in recent_calls if 'forwarded' not in call.to_dict()]
        
        print(f"Found {len(calls)} calls to forward")
        
        # Forward each call
        forwarded_count = 0
        for call_doc in calls:
            call_data = call_doc.to_dict()
            call_id = call_doc.id
            
            # Skip calls with UNKNOWN symbols
            if call_data.get('symbol', call_data.get('token', '')) == 'UNKNOWN':
                print(f"⚠️ Skipping call {call_id} with UNKNOWN symbol")
                # Mark as forwarded to avoid future processing
                calls_ref.document(call_id).update({"forwarded": True})
                continue
            
            print(f"Processing call {call_id}: {call_data.get('symbol', call_data.get('token', 'UNKNOWN'))}")
            
            # Format message
            message = await format_call_message(call_data)
            
            # Send to all chats
            success = True
            for chat_id in CHAT_IDS:
                result = await send_message_to_telegram(client, chat_id, message)
                success = success and result
            
            # Mark as forwarded regardless of success to avoid spamming on retry
            # But add success status to the record
            calls_ref.document(call_id).update({
                "forwarded": True,
                "forwardSuccess": success,
                "forwardTimestamp": firestore.SERVER_TIMESTAMP
            })
            
            if success:
                print(f"✅ Successfully forwarded call {call_id}")
                forwarded_count += 1
            
            # Wait between forwards to avoid rate limiting
            await asyncio.sleep(1)
        
        print(f"✅ Forwarding complete! Forwarded {forwarded_count} calls")
    
    except Exception as e:
        print(f"❌ Error during forwarding: {e}")
    
    finally:
        # Disconnect client
        if client:
            try:
                await client.disconnect()
                print("👋 Disconnected from Telegram")
            except Exception as e:
                print(f"⚠️ Error disconnecting: {e}")

if __name__ == "__main__":
    # Allow running as a scheduled task
    while True:
        print(f"\n===== {time.strftime('%Y-%m-%d %H:%M:%S')} =====")
        asyncio.run(forward_new_calls())
        
        # Ask if we should continue running in loop or exit
        if len(sys.argv) <= 1 or sys.argv[1] != "--loop":
            choice = input("\nRun again? (y/n, or enter minutes to wait): ")
            if choice.lower() == 'n':
                break
            elif choice.lower() == 'y':
                continue
            elif choice.isdigit():
                wait_time = int(choice) * 60
                print(f"Waiting {wait_time} seconds before next run...")
                time.sleep(wait_time)
            else:
                break
        else:
            # When run with --loop, wait 5 minutes between checks
            print("Running in loop mode. Waiting 5 minutes before next check...")
            time.sleep(300) 
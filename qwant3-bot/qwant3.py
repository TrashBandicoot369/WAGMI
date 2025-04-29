from telethon import TelegramClient, events
from telethon.errors import ChannelPrivateError
from telethon.tl.types import PeerChannel
import re
import asyncio
import time
import random
import logging
import os
import signal
import sys
import firebase_admin
from firebase_admin import credentials, firestore

# Configure logging with timestamps
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("qwant_bot")

# Initialize Firebase
try:
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    logger.info("✅ Firebase initialized successfully")
except Exception as e:
    logger.error(f"❌ Firebase initialization error: {e}")
    raise e

# TEST MODE FLAG
TEST_MODE = False

def format_number(num):
    if num >= 1_000_000:
        return f"{num/1_000_000:.2f}M"
    elif num >= 1_000:
        return f"{num/1_000:.2f}K"
    else:
        return f"{num:.2f}"

# List of bot usernames to monitor
BOT_USERNAMES = ["RickBurpBot", "PhanesGreenBot", "pocketprotectorbot", "SniperUniversityBot", "thelostsole_bot", "DexTools_Bot"]

# Telegram API credentials
API_ID_1 = 29312830
API_HASH_1 = "24622c388a689db6cf871903fdca8c1c"

# Track these groups with client 1 only
SOURCE_GROUPS_CLIENT1 = [-1001758236818, -1002238854475, -1002179220327, -1002554339683]  # The Sauna, PBC Lounge, Sniper University, PumpFun Unfiltered
DESTINATION_GROUPS = [-1002416386782, -1002651955296]

ALL_SOURCE_GROUPS = SOURCE_GROUPS_CLIENT1

# Authorized users mapping
USER_MAPPING = {}
SHOT_CALLERS = []
CALLERS = []

# Contract address patterns
SOLANA_ADDRESS_PATTERN = r"([1-9A-HJ-NP-Za-km-z]{32,44})"
CONTRACT_ADDRESS_PATTERN = r"(0x[a-fA-F0-9]{40}|[1-9A-HJ-NP-Za-km-z]{32,44})"

# Add semaphore for preventing concurrent Telegram client operations
telegram_semaphore = asyncio.Semaphore(1)

# Add health check variables for monitoring
last_activity_time = time.time()
health_status = "STARTING"

def handle_sigterm(signum, frame):
    """Handle SIGTERM signal gracefully to ensure proper cleanup"""
    logger.info("🛑 Received SIGTERM signal, shutting down gracefully...")
    health_status = "STOPPING"
    # Disconnect clients if they're connected
    if client1.is_connected():
        client1.disconnect()
    logger.info("👋 Bot stopped gracefully")
    sys.exit(0)

signal.signal(signal.SIGTERM, handle_sigterm)
signal.signal(signal.SIGINT, handle_sigterm)

def update_activity():
    """Update the last activity timestamp for health monitoring"""
    global last_activity_time
    last_activity_time = time.time()

def load_users():
    global USER_MAPPING, SHOT_CALLERS, CALLERS
    USER_MAPPING.clear()
    SHOT_CALLERS.clear()
    CALLERS.clear()
    
    try:
        # Get users from the roles collection
        roles_ref = db.collection("roles")
        roles_docs = roles_ref.stream()
        users_loaded = 0
        shot_caller_list = []
        caller_list = []
        
        for doc in roles_docs:
            try:
                users_loaded += 1
                user_data = doc.to_dict()
                uid = int(doc.id)
                
                # Get username - check both 'username' and 'name' fields
                username = user_data.get('username') or user_data.get('name')
                if not username:
                    logger.warning(f"⚠️ No username found for user {uid}, data: {user_data}")
                    username = f"Unknown-{uid}"
                
                # Get role, default to CALLER if not specified
                role = user_data.get('role', 'CALLER').upper()
                
                # Store the mapping
                USER_MAPPING[uid] = username
                
                # Add to appropriate list
                if role == "SHOT_CALLER":
                    SHOT_CALLERS.append(uid)
                    shot_caller_list.append(f"@{username}")
                    logger.info(f"📊 Added Shot Caller: @{username} (ID: {uid})")
                else:
                    CALLERS.append(uid)
                    caller_list.append(f"@{username}")
                    logger.info(f"📊 Added Caller: @{username} (ID: {uid})")
            except Exception as e:
                logger.error(f"❌ Error processing user document {doc.id}: {e}")
                continue
        
        # Print startup summary with icons
        startup_message = "\n" + "="*50 + "\n"
        startup_message += "🤖 QWANT BOT STARTUP SUMMARY\n"
        startup_message += "="*50 + "\n"
        startup_message += f"📊 Total Users Loaded: {len(USER_MAPPING)}\n\n"
        
        # Format shot callers list
        if shot_caller_list:
            startup_message += "🎯 SHOT CALLERS:\n"
            for username in sorted(shot_caller_list):
                startup_message += f"   • {username}\n"
        else:
            startup_message += "🎯 SHOT CALLERS: None\n"
        
        startup_message += "\n"
        
        # Format regular callers list
        if caller_list:
            startup_message += "👥 REGULAR CALLERS:\n"
            for username in sorted(caller_list):
                startup_message += f"   • {username}\n"
        else:
            startup_message += "👥 REGULAR CALLERS: None\n"
        
        startup_message += "\n"
        startup_message += f"🔍 Monitoring Groups: {len(SOURCE_GROUPS_CLIENT1)}\n"
        startup_message += f"📢 Forwarding Groups: {len(DESTINATION_GROUPS)}\n"
        startup_message += "="*50
        logger.info(startup_message)
        
        # Log warning if no users were loaded
        if users_loaded == 0:
            logger.warning("⚠️ No users found in Firebase roles collection!")
            if TEST_MODE:
                test_id = 1234567890
                USER_MAPPING[test_id] = "test_user"
                SHOT_CALLERS.append(test_id)
                logger.info(f"📊 Added test user with ID {test_id}")
    except Exception as e:
        logger.error(f"❌ Error loading users from Firebase: {e}")
        import traceback
        traceback.print_exc()

# Function to reload users periodically
async def periodic_user_reload():
    while True:
        try:
            await asyncio.sleep(300)  # Reload every 5 minutes
            logger.info("\n🔄 Reloading user roles from Firebase...")
            
            # Store previous state for comparison
            previous_users = USER_MAPPING.copy()
            previous_shot_callers = set(SHOT_CALLERS)
            previous_callers = set(CALLERS)
            
            # Reload users
            load_users()
            
            # Check for changes
            new_users = set(USER_MAPPING.keys()) - set(previous_users.keys())
            removed_users = set(previous_users.keys()) - set(USER_MAPPING.keys())
            role_changes = {uid for uid in USER_MAPPING if uid in previous_users and 
                          ((uid in SHOT_CALLERS) != (uid in previous_shot_callers))}
            
            if new_users or removed_users or role_changes:
                logger.info("\n📈 User Changes Detected:")
                
                if new_users:
                    logger.info("➕ New Users:")
                    for uid in new_users:
                        logger.info(f"   • @{USER_MAPPING[uid]}")
                
                if removed_users:
                    logger.info("➖ Removed Users:")
                    for uid in removed_users:
                        logger.info(f"   • @{previous_users[uid]}")
                
                if role_changes:
                    logger.info("🔄 Role Changes:")
                    for uid in role_changes:
                        new_role = "SHOT CALLER" if uid in SHOT_CALLERS else "CALLER"
                        old_role = "SHOT CALLER" if uid in previous_shot_callers else "CALLER"
                        logger.info(f"   • @{USER_MAPPING[uid]}: {old_role} → {new_role}")
            else:
                logger.info("✅ User roles reloaded - No changes detected")
        except Exception as e:
            logger.error(f"❌ Error in periodic user reload: {e}")
            await asyncio.sleep(60)

# Use the original session names
client1 = TelegramClient(
    "user_session1", 
    API_ID_1, 
    API_HASH_1,
    connection_retries=10,
    retry_delay=1
)

def identify_chain(contract_address):
    """Identify which blockchain the contract is from based on address format"""
    if re.match(r"^0x[a-fA-F0-9]{40}$", contract_address):
        return "ethereum"
    elif re.match(r"^[1-9A-HJ-NP-Za-km-z]{32,44}$", contract_address):
        return "solana"
    else:
        return "solana"

def create_handler(client_name):
    async def handler(event):
        # Update activity timestamp for health monitoring
        update_activity()
        
        try:
            logger.info(f"\n🔔 EVENT RECEIVED for {client_name} - Chat ID: {event.chat_id}")
            
            # Check if this is a message event
            if not hasattr(event, 'message') or not hasattr(event.message, 'text'):
                logger.warning(f"⚠️ Event doesn't contain a text message, skipping")
                return
                
            # Check if the message is in a monitored group
            if client_name == "client1" and event.chat_id not in SOURCE_GROUPS_CLIENT1:
                logger.warning(f"⚠️ Message from non-monitored group {event.chat_id}, skipping")
                return
                
            logger.info(f"\n🔔 HANDLER TRIGGERED for {client_name} - Chat ID: {event.chat_id}")
            
            # Get chat and sender info
            chat = await event.get_chat()
            sender = await event.get_sender()
            username = USER_MAPPING.get(sender.id, sender.username or "Unknown")

            # Check authorization status first
            is_authorized = sender.id in CALLERS + SHOT_CALLERS
            is_shot_caller = sender.id in SHOT_CALLERS
            auth_status = "🟢 AUTHORIZED" if is_authorized else "🔴 UNAUTHORIZED"
            user_type = "SHOT CALLER" if is_shot_caller else "CALLER" if sender.id in CALLERS else "UNAUTHORIZED"
            
            logger.info(f"\n👤 User: @{username} (ID: {sender.id})")
            logger.info(f"🔑 Authorization: {auth_status} - Type: {user_type}")
            logger.info(f"📝 Message: {event.message.text[:100]}...")

            # Skip bot messages
            if hasattr(sender, 'username') and sender.username in BOT_USERNAMES:
                logger.info(f"⏭️ Skipping message from bot {sender.username}")
                return

            # Check for contract address
            ca_match = re.search(CONTRACT_ADDRESS_PATTERN, event.message.text)
            
            if not ca_match:
                logger.info("⏭️ Skipping message without contract address")
                return
                
            found_contract = ca_match.group(1)
            logger.info(f"✅ Contract found: {found_contract}")
            
            # Only proceed if user is authorized
            if not is_authorized:
                logger.warning(f"⛔ Skipping unauthorized message from {username} (ID: {sender.id})")
                return
            
            # Identify chain and create dex URL
            chain = identify_chain(found_contract)
            dex_url = f"https://dexscreener.com/solana/{found_contract}" if chain == "solana" else f"https://dexscreener.com/ethereum/{found_contract}"
            
            # Forward the message
            header = "🧠💥 BIG BRAIN CALL 💥🧠" if is_shot_caller else "🚨 ALERT 🚨"
            
            msg = (
                f"{header}\n"
                f"Group: {chat.title}\n"
                f"User: @{username} ({user_type})\n"
                f"Chain: {chain.upper()}\n"
                f"DEX: {dex_url}\n\n"
                f"Message:\n{event.message.text}"
            )

            # Forward to appropriate groups
            for group_id in DESTINATION_GROUPS:
                try:
                    # Only forward to shot caller group (-1002651955296) if user is a shot caller
                    if group_id == -1002651955296:
                        if is_shot_caller:
                            await event.client.send_message(group_id, msg)
                            logger.info(f"✅ Forwarded to SHOT CALLER group {group_id}")
                        else:
                            logger.info(f"⏭️ Skipping shot caller group for non-shot caller")
                            continue
                    else:
                        # Forward to regular group
                        await event.client.send_message(group_id, msg)
                        logger.info(f"✅ Forwarded to regular group {group_id}")
                except Exception as e:
                    logger.error(f"❌ Error forwarding to group {group_id}: {e}")
            
            return

        except Exception as e:
            logger.error(f"❌ Handler error: {e}")
            import traceback
            traceback.print_exc()
    return handler

async def test_group_access():
    logger.info("🧪 Testing group access...")
    for group_id in SOURCE_GROUPS_CLIENT1:
        try:
            messages = await client1.get_messages(group_id, limit=1)
            if messages and len(messages) > 0:
                logger.info(f"✅ Client1 can access group {group_id} - Latest message: {messages[0].text[:30]}...")
            else:
                logger.warning(f"⚠️ Client1 can access group {group_id} but no messages found")
        except Exception as e:
            logger.error(f"❌ Client1 CANNOT access group {group_id}: {e}")
    logger.info("🧪 Group access test completed")

async def health_check_server():
    """Run a simple health check server for Railway/Docker monitoring"""
    global health_status
    
    from aiohttp import web
    
    async def handle_health(request):
        client1_ok = client1.is_connected()
        activity_ok = (time.time() - last_activity_time) < 600
        
        status = {
            "status": health_status,
            "uptime": time.time() - start_time,
            "client1": "connected" if client1_ok else "disconnected",
            "last_activity": int(time.time() - last_activity_time),
            "activity_ok": activity_ok
        }
        
        http_status = 200 if client1_ok and activity_ok else 500
        return web.json_response(status, status=http_status)
    
    app = web.Application()
    app.add_routes([web.get('/health', handle_health)])
    
    port = int(os.environ.get('PORT', 8080))
    logger.info(f"🏥 Starting health check server on port {port}")
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    
    health_status = "RUNNING"
    logger.info(f"✅ Health check server running on http://0.0.0.0:{port}/health")

async def main():
    logger.info("🚀 Starting bot...")
    
    global start_time
    start_time = time.time()
    
    # Start health check server
    asyncio.create_task(health_check_server())
    
    # Start periodic user reload
    asyncio.create_task(periodic_user_reload())
    
    # Run client1
    await run_client(client1, "client1", SOURCE_GROUPS_CLIENT1)

async def run_client(client, client_name, source_groups):
    try:
        logger.info(f"⏳ Starting {client_name}...")
        await client.start()
        logger.info(f"✅ {client_name} connected!")
        
        # Add reconnection logic
        client.loop.create_task(maintain_connection(client, client_name))
        
        # Test the connection
        me = await client.get_me()
        logger.info(f"✅ {client_name} authenticated as {me.username or me.id}")
        
        # Add event handler
        handler_function = create_handler(client_name)
        
        if source_groups:
            # Test access to each group
            for group_id in source_groups:
                try:
                    entity = await client.get_entity(group_id)
                    logger.info(f"✅ {client_name} successfully accessed group {group_id} ({entity.title})")
                except Exception as e:
                    logger.error(f"❌ {client_name} CANNOT access group {group_id}: {e}")
            
            logger.info(f"🔄 Registering event handler for {client_name}...")
            client.add_event_handler(
                handler_function,
                events.NewMessage(chats=source_groups)
            )
            logger.info(f"📡 {client_name} monitoring ONLY these {len(source_groups)} groups: {source_groups}")
            
            handlers = client.list_event_handlers()
            logger.info(f"✅ Total handlers for {client_name}: {len(handlers)}")
            for handler in handlers:
                logger.info(f"  - Handler: {handler}")
        else:
            logger.warning(f"⚠️ {client_name} has no groups to monitor")
        
        logger.info(f"🚀 {client_name} is now running and listening for events...")
        await client.run_until_disconnected()
        
    except Exception as e:
        logger.error(f"❌ {client_name} error: {e}")
        import traceback
        traceback.print_exc()

async def maintain_connection(client, client_name):
    """Periodically check connection and reconnect if needed"""
    while True:
        try:
            await asyncio.sleep(300)  # Check every 5 minutes
            
            if not client.is_connected():
                logger.warning(f"⚠️ {client_name} connection lost, attempting to reconnect...")
                await client.connect()
                if await client.is_user_authorized():
                    logger.info(f"✅ {client_name} reconnected successfully")
                else:
                    logger.error(f"❌ {client_name} reconnected but not authorized")
            else:
                await client.get_me()
                logger.debug(f"✅ {client_name} connection verified")
        except Exception as e:
            logger.error(f"❌ Error maintaining {client_name} connection: {e}")
            await asyncio.sleep(60)

if __name__ == "__main__":
    start_time = time.time()
    
    logger.info(f"\n🚀 Starting QWANT3 Telegram Bot v1.3 at {time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"🔧 Configuration:")
    logger.info(f"  - SOURCE_GROUPS_CLIENT1: {SOURCE_GROUPS_CLIENT1}")
    logger.info(f"  - DESTINATION_GROUPS: {DESTINATION_GROUPS}")
    logger.info(f"  - Running in {'TEST' if TEST_MODE else 'PRODUCTION'} mode")
    
    if os.environ.get('RAILWAY_ENVIRONMENT'):
        logger.info(f"🚂 Running in Railway environment: {os.environ.get('RAILWAY_ENVIRONMENT')}")
    
    # Load initial users and show startup banner
    load_users()
    
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_group_access())
    
    try:
        logger.info("\n🔄 Starting main client loop...")
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        logger.info("\n👋 Bot stopped by user")
    except Exception as e:
        logger.error(f"\n❌ Main loop error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        logger.info("\n🛑 Bot stopped")

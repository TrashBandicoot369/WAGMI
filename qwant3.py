from telethon import TelegramClient, events
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.errors import ChannelPrivateError
from firebase_admin import firestore
import re
import asyncio
from lib.tokenResolver import resolve_token_metadata, retry_unknown_tokens
from lib.firebase_admin_setup import db

# --- Helper Functions ---
BOT_USERNAMES = ["RickBurpBot", "PhanesGreenBot", "pocketprotectorbot"]

def parse_number(value):
    try:
        # Remove any non-numeric characters except for K, M, B, and decimal points
        value = value.strip()
        
        # Handle percentage signs if present
        if "%" in value:
            value = value.replace("%", "")
            # Return as decimal percentage (e.g., 25% → 0.25)
            return float(value) / 100
        
        # Convert to uppercase for consistent handling
        value = value.upper()
        
        # Handle K (thousands)
        if "K" in value:
            multiplier = 1000
            value = value.replace("K", "")
        # Handle M (millions)
        elif "M" in value:
            multiplier = 1000000
            value = value.replace("M", "")
        # Handle B (billions)
        elif "B" in value:
            multiplier = 1000000000
            value = value.replace("B", "")
        else:
            multiplier = 1
        
        # Remove commas and any remaining non-numeric characters except decimal points
        value = re.sub(r'[^0-9\.]', '', value)
        
        # Convert to float and apply multiplier
        return int(float(value) * multiplier)
    except Exception as e:
        print(f"❌ Error parsing number '{value}': {e}")
        return 0

async def parse_bot_message(event, target_ca):
    sender = await event.get_sender()
    print(f"🔍 Parsing message from {sender.username}")
    
    if sender.username not in BOT_USERNAMES:
        print(f"❌ Sender {sender.username} not in BOT_USERNAMES")
        return None

    content = event.text if hasattr(event, 'text') else event.message.text
    print(f"📄 Parsing content with length {len(content)}")
    
    if target_ca not in content:
        print(f"❌ Target CA {target_ca} not found in content")
        return None

    try:
        print(f"🔍 Running regex matches on bot content...")
        symbol = "UNKNOWN"
        marketCap = 0
        athMarketCap = 0
        volume24h = 0
        priceUsd = 0
        
        # First look for token symbol - multiple bot formats
        if sender.username == "RickBurpBot":
            # RickBurpBot format: [**Fartcoin Killer**]... **$FEBREZE**
            symbol_match = re.search(r"\*\*\$([\w]+)\*\*", content)
            if not symbol_match:
                # Try secondary format (token name without $)
                name_match = re.search(r"\*\*([\w\s]+)\*\*", content)
                if name_match:
                    symbol = name_match.group(1).split()[-1]  # Last word is often the ticker
            else:
                symbol = symbol_match.group(1)
                
            # Market cap format: FDV: `$130K`
            fdv_match = re.search(r"FDV: `\$([\d\.KMB]+)`", content)
            if fdv_match:
                marketCap = parse_number(fdv_match.group(1))
                
            # ATH format: ATH: `$172K`
            ath_match = re.search(r"ATH: `\$([\d\.KMB]+)`", content)
            if ath_match:
                athMarketCap = parse_number(ath_match.group(1))
                
            # Volume format: Vol: `$283K`
            vol_match = re.search(r"Vol: `\$([\d\.KMB]+)`", content)
            if vol_match:
                volume24h = parse_number(vol_match.group(1))
                
            # Price format: USD: `$0.0001298`
            price_match = re.search(r"USD: `\$([\d\.]+)`", content)
            if price_match:
                priceUsd = float(price_match.group(1))
        
        elif sender.username == "PhanesGreenBot":
            # PhanesGreenBot format: [**Fartcoin Killer**]... ($FEBREZE)
            symbol_match = re.search(r"\$([A-Za-z0-9]+)\)", content)
            if symbol_match:
                symbol = symbol_match.group(1)
            else:
                # Try another format without parentheses
                symbol_match = re.search(r"\$([\w]+)", content)
                if symbol_match:
                    symbol = symbol_match.group(1)
                    
            # Market cap format: MC:   `**$144.4K**`
            mc_match = re.search(r"MC:\s+`\*\*\$([\d\.KMB]+)\*\*`", content)
            if mc_match:
                marketCap = parse_number(mc_match.group(1))
                
            # ATH format: ATH:  `**$175.7K**`
            ath_match = re.search(r"ATH:\s+`\*\*\$([\d\.KMB]+)\*\*`", content)
            if ath_match:
                athMarketCap = parse_number(ath_match.group(1))
                
            # Volume format: Vol:  `**$285.5K**`
            vol_match = re.search(r"Vol:\s+`\*\*\$([\d\.KMB]+)\*\*`", content)
            if vol_match:
                volume24h = parse_number(vol_match.group(1))
                
            # Price format: USD:  `**$0.0001444**`
            price_match = re.search(r"USD:\s+`\*\*\$([\d\.]+)\*\*`", content)
            if price_match:
                priceUsd = float(price_match.group(1))
        
        # If still couldn't parse, try generic patterns
        if symbol == "UNKNOWN":
            print("⚠️ Using generic symbol pattern fallback")
            # Look for $SYMBOL pattern
            symbol_match = re.search(r"\$([A-Z0-9]{3,10})", content, re.IGNORECASE)
            if symbol_match:
                symbol = symbol_match.group(1)
        
        if marketCap == 0:
            print("⚠️ Using generic market cap pattern fallback")
            # Try various market cap formats
            mc_patterns = [
                r"MC:?\s*\$?([\d\.KMB]+)", 
                r"FDV:?\s*\$?([\d\.KMB]+)",
                r"marketcap:?\s*\$?([\d\.KMB]+)",
                r"cap:?\s*\$?([\d\.KMB]+)"
            ]
            for pattern in mc_patterns:
                mc_match = re.search(pattern, content, re.IGNORECASE)
                if mc_match:
                    marketCap = parse_number(mc_match.group(1))
                    break
        
        print(f"🔍 Parsed values: Symbol={symbol}, MC=${marketCap}, ATH=${athMarketCap}, Vol=${volume24h}, Price=${priceUsd}")
        
        metadata = {
            "symbol": symbol,
            "contract": target_ca,
            "marketCap": marketCap,
            "athMarketCap": athMarketCap,
            "volume24h": volume24h,
            "priceUsd": priceUsd,
            "dexUrl": f"https://pump.fun/{target_ca}",
            "source": "bot",
            "timestamp": firestore.SERVER_TIMESTAMP
        }

        print(f"✅ Bot resolution result: {metadata}")
        return metadata

    except Exception as e:
        print(f"❌ Failed to parse bot message: {type(e).__name__} - {e}")
        import traceback
        traceback.print_exc()
        return None

async def wait_for_bot_response(client, chat_id, target_ca, timeout=15):
    future = asyncio.get_event_loop().create_future()
    print(f"🔍 Setting up bot listener for {target_ca} in {chat_id} with {timeout}s timeout")

    @client.on(events.NewMessage(chats=chat_id))
    async def bot_listener(event):
        sender = await event.get_sender()
        print(f"👂 Received message from {sender.username or sender.id}")
        
        if sender.username in BOT_USERNAMES:
            print(f"🤖 Message from tracked bot: {sender.username}")
            
            # Print first 100 chars of message for debugging
            msg_preview = event.message.text[:100] + "..." if len(event.message.text) > 100 else event.message.text
            print(f"📝 Bot message preview: {msg_preview}")
            
            if target_ca in event.message.text:
                print(f"✅ Found target contract in bot message!")
                if not future.done():
                    future.set_result(event)
            else:
                print(f"❌ Target contract not found in bot message")

    try:
        print(f"⏳ Waiting up to {timeout}s for bot response...")
        await asyncio.wait_for(future, timeout)
        print(f"✅ Bot response received within timeout")
        return future.result()
    except asyncio.TimeoutError:
        print(f"⌛ No bot response for {target_ca} within {timeout}s timeout")
        return None

async def save_or_update_token(contract, metadata, db, is_shot_caller=False):
    """Save or update token metadata to Firestore"""
    # Add token-specific fields
    metadata["token"] = metadata.get("symbol", "UNKNOWN")
    metadata["volume"] = metadata.get("volume24h", 0)
    metadata["initialMarketCap"] = metadata.get("marketCap", 0)
    metadata["percentChange24h"] = 0
    metadata["capChange"] = 0
    metadata["updated"] = firestore.SERVER_TIMESTAMP
    metadata["lastRefreshed"] = firestore.SERVER_TIMESTAMP
    metadata["shotCaller"] = is_shot_caller
    
    # Add Twitter and socials if available
    if metadata.get("twitter"):
        socials = {"twitter": metadata["twitter"]}
        if metadata.get("website"):
            socials["website"] = metadata["website"]
        metadata["socials"] = socials
    else:
        metadata["twitter"] = None

    print(f"📦 Pushing to Firestore: {metadata}")
    try:
        doc_ref = calls_ref.add(metadata)
        print(f"🔥 Firestore write succeeded. Document ref: {doc_ref}")
        return True
    except Exception as e:
        print(f"❌ Firestore write FAILED: {type(e).__name__} - {e}")
        return False

# --- Firebase ---
calls_ref = db.collection("calls")
users_ref = db.collection("telegramUsers")

# --- Telegram API Setup ---
API_ID_1 = 29312830
API_HASH_1 = "24622c388a689db6cf871903fdca8c1c"
API_ID_2 = 26108909
API_HASH_2 = "3cb55b9919cee50e576611641283ec5a"

SOURCE_GROUPS_CLIENT1 = [-1002048135645, -1002238854475, 2179220327]
SOURCE_GROUPS_CLIENT2 = [-1001758236818]
DESTINATION_GROUPS = [-1002416386782, -1002651955296]

# Initialize user roles from Firestore
USER_MAPPING = {}
SHOT_CALLERS = []
CALLERS = []

def load_users():
    global USER_MAPPING, SHOT_CALLERS, CALLERS
    USER_MAPPING.clear()
    SHOT_CALLERS.clear()
    CALLERS.clear()

    user_docs = users_ref.stream()
    for doc in user_docs:
        uid = int(doc.id)
        user = doc.to_dict()
        username = user.get("username", "Unknown")
        role = user.get("role", "CALLER")
        USER_MAPPING[uid] = username
        if role == "SHOT_CALLER":
            SHOT_CALLERS.append(uid)
        else:
            CALLERS.append(uid)

    print(f"📊 Loaded {len(USER_MAPPING)} users: {len(SHOT_CALLERS)} shot callers, {len(CALLERS)} callers")

load_users()

client1 = TelegramClient("user_session1", API_ID_1, API_HASH_1)
client2 = TelegramClient("user_session2", API_ID_2, API_HASH_2)

def create_handler(source_groups):
    async def handler(event):
        try:
            chat = await event.get_chat()
            sender = await event.get_sender()
            print(f"\n📥 MESSAGE RECEIVED from {sender.username or sender.id} in {chat.title}")
            print(f"📝 Content:\n{event.message.text}\n")

            if sender.id not in CALLERS + SHOT_CALLERS:
                print("⛔ User not authorized.")
                return

            username = USER_MAPPING.get(sender.id, sender.username or "Unknown")
            username_display = f"@{username}" if username != "Unknown" else "Unknown"
            is_shot_caller = sender.id in SHOT_CALLERS

            ca_match = re.search(r"(0x[a-fA-F0-9]{40}|[A-Za-z0-9]{25,44})", event.message.text)
            if not ca_match:
                print("❌ No contract address found.")
                return

            contract = ca_match.group(1)
            
            # Get detailed token metadata instead of just symbol
            token_metadata = await resolve_token_metadata(contract, db)
            
            # If we couldn't get metadata, try bot fallback
            if not token_metadata or token_metadata.get("symbol", "UNKNOWN") == "UNKNOWN":
                print(f"⚡ Resolution failed for {contract}, checking for bot fallback...")
                
                # First check if there are recent bot messages with this contract
                print("🔍 Checking recent messages for bot responses...")
                
                # Get recent messages from this chat
                try:
                    recent_messages = await event.client.get_messages(
                        entity=event.chat_id,
                        limit=10  # Check last 10 messages
                    )
                    
                    # Check if any of these messages are from bots and contain our contract
                    bot_event = None
                    for msg in recent_messages:
                        if msg.sender_id != sender.id:  # Skip the original user's message
                            msg_sender = await event.client.get_entity(msg.sender_id)
                            if hasattr(msg_sender, 'username') and msg_sender.username in BOT_USERNAMES and contract in msg.text:
                                print(f"✅ Found existing bot message from {msg_sender.username}")
                                bot_event = msg
                                break
                    
                    # If we found an existing bot message, process it
                    if bot_event:
                        print(f"🤖 Processing existing bot message...")
                        bot_metadata = await parse_bot_message(bot_event, contract)
                        if bot_metadata:
                            print(f"✅ Successfully parsed bot metadata: {bot_metadata}")
                            
                            # Prepare full metadata for Firebase
                            full_metadata = {
                                # Core token info
                                "symbol": bot_metadata.get("symbol", "UNKNOWN"),
                                "token": bot_metadata.get("symbol", "UNKNOWN"),
                                "contract": contract,
                                "dexUrl": bot_metadata.get("dexUrl", f"https://pump.fun/{contract}"),
                                
                                # Market data
                                "marketCap": bot_metadata.get("marketCap", 0),
                                "volume24h": bot_metadata.get("volume24h", 0),
                                "volume": bot_metadata.get("volume24h", 0),
                                "initialMarketCap": bot_metadata.get("marketCap", 0),
                                "athMarketCap": bot_metadata.get("athMarketCap", bot_metadata.get("marketCap", 0)),
                                "priceUsd": bot_metadata.get("priceUsd", 0),
                                
                                # Change calculations
                                "percentChange24h": 0,
                                "capChange": 0,
                                
                                # Timestamps
                                "timestamp": firestore.SERVER_TIMESTAMP,
                                "updated": firestore.SERVER_TIMESTAMP,
                                "lastRefreshed": firestore.SERVER_TIMESTAMP,
                                
                                # User data
                                "shotCaller": is_shot_caller,
                                
                                # Source tracking
                                "source": "bot",
                                "bot": bot_event.sender.username if hasattr(bot_event, 'sender') and hasattr(bot_event.sender, 'username') else "unknown"
                            }
                            
                            # Add Twitter if available
                            twitter_match = re.search(r"\[🐦\]\((https://x\.com/.*?)\)", bot_event.text)
                            if twitter_match:
                                handle = twitter_match.group(1).split('/')[-1]
                                full_metadata["twitter"] = handle
                                
                                # Add socials object
                                socials = {"twitter": handle}
                                
                                # Look for website
                                website_match = re.search(r"\[💬\]\((https://t\.me/.*?)\)", bot_event.text)
                                if website_match:
                                    socials["website"] = website_match.group(1)
                                    
                                full_metadata["socials"] = socials
                            
                            # Push to Firebase
                            print(f"🔥 Pushing bot-resolved data to Firebase: {full_metadata}")
                            try:
                                doc_ref = calls_ref.add(full_metadata)
                                print(f"✅ Firebase write SUCCESS. Document ID: {doc_ref[1].id}")
                                
                                # Create alert message
                                token = full_metadata.get("symbol", "UNKNOWN")
                                market_cap = full_metadata.get("marketCap", 0)
                                
                                header = "🧠💥 BIG BRAIN CALL 💥🧠" if is_shot_caller else "🚨 ALERT 🚨"
                                msg = (
                                    f"{header}\n"
                                    f"Group: {chat.title}\n"
                                    f"User: {username_display} (ID: {sender.id})\n"
                                    f"Token: {token}\n"
                                    f"Market Cap: ${format_number(market_cap)}\n"
                                    f"Message:\n{event.message.text}"
                                )

                                for group_id in DESTINATION_GROUPS:
                                    if group_id == -1002651955296 and sender.id not in SHOT_CALLERS:
                                        continue
                                    try:
                                        await event.client.send_message(group_id, msg)
                                        print(f"✅ Sent to {group_id}")
                                    except Exception as e:
                                        print(f"❌ Error sending: {e}")
                                return
                            except Exception as e:
                                print(f"❌ Firebase write FAILED: {type(e).__name__} - {e}")
                except Exception as e:
                    print(f"❌ Error checking recent messages: {type(e).__name__} - {e}")
                
                # If we couldn't find an existing bot message, wait for a new one
                print("🔄 No existing bot messages found, waiting for new ones...")
                bot_event = await wait_for_bot_response(event.client, event.chat_id, contract)
                if bot_event:
                    print(f"🤖 Bot response found, parsing metadata...")
                    bot_metadata = await parse_bot_message(bot_event, contract)
                    if bot_metadata:
                        print(f"✅ Successfully parsed bot metadata: {bot_metadata}")
                        
                        # Prepare full metadata for Firebase
                        full_metadata = {
                            # Core token info
                            "symbol": bot_metadata.get("symbol", "UNKNOWN"),
                            "token": bot_metadata.get("symbol", "UNKNOWN"),
                            "contract": contract,
                            "dexUrl": bot_metadata.get("dexUrl", f"https://pump.fun/{contract}"),
                            
                            # Market data
                            "marketCap": bot_metadata.get("marketCap", 0),
                            "volume24h": bot_metadata.get("volume24h", 0),
                            "volume": bot_metadata.get("volume24h", 0),
                            "initialMarketCap": bot_metadata.get("marketCap", 0),
                            "athMarketCap": bot_metadata.get("athMarketCap", bot_metadata.get("marketCap", 0)),
                            "priceUsd": bot_metadata.get("priceUsd", 0),
                            
                            # Change calculations
                            "percentChange24h": 0,
                            "capChange": 0,
                            
                            # Timestamps
                            "timestamp": firestore.SERVER_TIMESTAMP,
                            "updated": firestore.SERVER_TIMESTAMP,
                            "lastRefreshed": firestore.SERVER_TIMESTAMP,
                            
                            # User data
                            "shotCaller": is_shot_caller,
                            
                            # Source tracking
                            "source": "bot",
                            "bot": bot_event.sender.username
                        }
                        
                        # Add Twitter if available
                        twitter_match = re.search(r"\[🐦\]\((https://x\.com/.*?)\)", bot_event.message.text)
                        if twitter_match:
                            handle = twitter_match.group(1).split('/')[-1]
                            full_metadata["twitter"] = handle
                            
                            # Add socials object
                            socials = {"twitter": handle}
                            
                            # Look for website
                            website_match = re.search(r"\[💬\]\((https://t\.me/.*?)\)", bot_event.message.text)
                            if website_match:
                                socials["website"] = website_match.group(1)
                                
                            full_metadata["socials"] = socials
                        
                        # Push to Firebase
                        print(f"🔥 Pushing bot-resolved data to Firebase: {full_metadata}")
                        try:
                            doc_ref = calls_ref.add(full_metadata)
                            print(f"✅ Firebase write SUCCESS. Document ID: {doc_ref[1].id}")
                            
                            # Create alert message
                            token = full_metadata.get("symbol", "UNKNOWN")
                            market_cap = full_metadata.get("marketCap", 0)
                            
                            header = "🧠💥 BIG BRAIN CALL 💥🧠" if is_shot_caller else "🚨 ALERT 🚨"
                            msg = (
                                f"{header}\n"
                                f"Group: {chat.title}\n"
                                f"User: {username_display} (ID: {sender.id})\n"
                                f"Token: {token}\n"
                                f"Market Cap: ${format_number(market_cap)}\n"
                                f"Message:\n{event.message.text}"
                            )

                            for group_id in DESTINATION_GROUPS:
                                if group_id == -1002651955296 and sender.id not in SHOT_CALLERS:
                                    continue
                                try:
                                    await event.client.send_message(group_id, msg)
                                    print(f"✅ Sent to {group_id}")
                                except Exception as e:
                                    print(f"❌ Error sending: {e}")
                            return
                        except Exception as e:
                            print(f"❌ Firebase write FAILED: {type(e).__name__} - {e}")
                
                print(f"❌ Could not resolve {contract} via any method.")
                # Schedule a retry for this token later
                asyncio.create_task(retry_single_token(contract))
                return
                
            token = token_metadata.get("symbol", "UNKNOWN")
            market_cap = token_metadata.get("marketCap", 0)
            volume = token_metadata.get("volume24h", 0)
            
            # Only proceed if we have valid data
            if token == "UNKNOWN" or market_cap == 0:
                print("❌ Invalid token data. Not creating call.")
                return

            # Create metadata object with all required fields matching Firestore screenshot
            metadata = {
                # Core token info
                "symbol": token,
                "token": token,
                "contract": contract,
                "dexUrl": f"https://dexscreener.com/solana/{contract}",
                
                # Market data
                "marketCap": market_cap,
                "volume24h": volume,
                "volume": volume,  # Keep both volume fields in sync
                "initialMarketCap": market_cap,
                "athMarketCap": market_cap,
                
                # Change calculations
                "percentChange24h": 0,
                "capChange": 0,
                
                # Timestamps
                "timestamp": firestore.SERVER_TIMESTAMP,
                "updated": firestore.SERVER_TIMESTAMP,
                "lastRefreshed": firestore.SERVER_TIMESTAMP,
                
                # User data
                "shotCaller": is_shot_caller
            }
            
            # Add Twitter handle if available
            if token_metadata.get("twitter"):
                metadata["twitter"] = token_metadata.get("twitter")
            else:
                metadata["twitter"] = None  # Explicitly set null as in screenshot
            
            # Add socials if available
            socials = {}
            if token_metadata.get("twitter"):
                socials["twitter"] = token_metadata.get("twitter")
            if token_metadata.get("website"):
                socials["website"] = token_metadata.get("website")
            
            if socials:
                metadata["socials"] = socials

            print(f"📦 Pushing to Firestore: {metadata}")
            try:
                doc_ref = calls_ref.add(metadata)
                print(f"🔥 Firestore write succeeded. Document ref: {doc_ref}")
            except Exception as e:
                print(f"❌ Firestore write FAILED: {type(e).__name__} - {e}")

            header = "🧠💥 BIG BRAIN CALL 💥🧠" if is_shot_caller else "🚨 ALERT 🚨"
            msg = (
                f"{header}\n"
                f"Group: {chat.title}\n"
                f"User: {username_display} (ID: {sender.id})\n"
                f"Token: {token}\n"
                f"Market Cap: ${format_number(market_cap)}\n"
                f"Message:\n{event.message.text}"
            )

            for group_id in DESTINATION_GROUPS:
                if group_id == -1002651955296 and sender.id not in SHOT_CALLERS:
                    continue
                try:
                    await event.client.send_message(group_id, msg)
                    print(f"✅ Sent to {group_id}")
                except ChannelPrivateError:
                    try:
                        await event.client(JoinChannelRequest(group_id))
                        await event.client.send_message(group_id, msg)
                    except Exception as e:
                        print(f"❌ Cannot join/send to {group_id}: {e}")
                except Exception as e:
                    print(f"❌ Error sending: {e}")
        except Exception as e:
            print(f"❌ Handler error: {e}")
    return handler

# Helper for formatting large numbers
def format_number(num):
    if num >= 1_000_000:
        return f"{num/1_000_000:.2f}M"
    elif num >= 1_000:
        return f"{num/1_000:.2f}K"
    else:
        return f"{num:.2f}"

# Function to retry a single token later
async def retry_single_token(contract, delay=300):  # 5 minutes delay
    print(f"⏳ Scheduling retry for token {contract} in {delay} seconds")
    await asyncio.sleep(delay)
    
    print(f"🔄 Retrying token resolution for {contract}")
    token_metadata = await resolve_token_metadata(contract, db, retries=3)
    
    if token_metadata and token_metadata.get("symbol", "UNKNOWN") != "UNKNOWN":
        print(f"✅ Successfully resolved token on retry: {token_metadata.get('symbol')}")
        # Find any calls with this contract address that need updating
        update_query = db.collection("calls").where("contract", "==", contract)
        docs = update_query.stream()
        
        for doc in docs:
            update_data = {
                "symbol": token_metadata.get("symbol"),
                "token": token_metadata.get("symbol"),
                "marketCap": token_metadata.get("marketCap", 0),
                "volume24h": token_metadata.get("volume24h", 0),
                "volume": token_metadata.get("volume24h", 0),
                "lastRefreshed": firestore.SERVER_TIMESTAMP
            }
            
            doc.reference.update(update_data)
            print(f"✅ Updated document for {contract}")
    else:
        print(f"❌ Still could not resolve token: {contract}")
        # Mark for bot resolution in the maintenance loop
        update_query = db.collection("calls").where("contract", "==", contract)
        docs = update_query.stream()
        
        for doc in docs:
            doc.reference.update({
                "needs_bot_resolution": True,
                "last_retry_attempt": firestore.SERVER_TIMESTAMP
            })
        print(f"🤖 Marked {contract} for bot resolution in next maintenance cycle")

client1.add_event_handler(
    create_handler(SOURCE_GROUPS_CLIENT1),
    events.NewMessage(chats=SOURCE_GROUPS_CLIENT1)
)

client2.add_event_handler(
    create_handler(SOURCE_GROUPS_CLIENT2),
    events.NewMessage(chats=SOURCE_GROUPS_CLIENT2)
)

async def maintenance_loop():
    """Regularly check for and retry unknown tokens"""
    while True:
        try:
            print("🔄 Running token maintenance loop...")
            await retry_unknown_tokens(db, max_tokens=10)
            
            # Check for tokens flagged for bot resolution
            print("🤖 Checking for tokens that need bot resolution...")
            bot_resolution_query = db.collection("calls").where("needs_bot_resolution", "==", True).limit(5)
            tokens_for_bots = bot_resolution_query.stream()
            
            for doc in tokens_for_bots:
                token_data = doc.to_dict()
                contract = token_data.get("contract")
                
                if not contract:
                    continue
                
                print(f"🤖 Attempting bot resolution for {contract}")
                
                # We need to use one of the clients to query a group where bots are active
                bot_groups = SOURCE_GROUPS_CLIENT1 + SOURCE_GROUPS_CLIENT2
                
                for chat_id in bot_groups:
                    try:
                        # Try to trigger bot response by sending contract message
                        trigger_msg = f"$check {contract}"
                        sent_msg = await client1.send_message(chat_id, trigger_msg)
                        
                        # Wait for bot response
                        bot_event = await wait_for_bot_response(client1, chat_id, contract)
                        if bot_event:
                            bot_metadata = await parse_bot_message(bot_event, contract)
                            if bot_metadata:
                                # Update token with bot data
                                update_data = {
                                    "symbol": bot_metadata.get("symbol"),
                                    "token": bot_metadata.get("symbol"),
                                    "marketCap": bot_metadata.get("marketCap", 0),
                                    "volume24h": bot_metadata.get("volume24h", 0),
                                    "volume": bot_metadata.get("volume24h", 0),
                                    "needs_bot_resolution": False,
                                    "lastRefreshed": firestore.SERVER_TIMESTAMP,
                                    "source": "bot"
                                }
                                
                                doc.reference.update(update_data)
                                print(f"✅ Bot resolved {contract} as {bot_metadata.get('symbol')}")
                                
                                # Delete our trigger message to keep channels clean
                                await sent_msg.delete()
                                break
                        
                        # If no response, delete our message and try next group
                        await sent_msg.delete()
                        
                    except Exception as e:
                        print(f"❌ Bot resolution error in group {chat_id}: {e}")
                        continue
            
            print("✅ Maintenance complete, sleeping for 30 minutes")
        except Exception as e:
            print(f"❌ Error in maintenance loop: {e}")
        
        # Run every 30 minutes
        await asyncio.sleep(1800)

async def main():
    print("🚀 Starting bot...")
    await client1.start()
    await client2.start()
    print("✅ Bot connected and listening.")
    
    # Start maintenance loop
    asyncio.create_task(maintenance_loop())
    
    await asyncio.gather(client1.run_until_disconnected(), client2.run_until_disconnected())

if __name__ == "__main__":
    asyncio.run(main())

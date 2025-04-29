import re
import asyncio
from telethon.sync import TelegramClient
from telethon.tl.types import PeerChannel
from firebase_admin import firestore

# Telegram API Config
api_id = 29312830
api_hash = "24622c388a689db6cf871903fdca8c1c"

# Session file must exist in your project root
client = TelegramClient('user_session1', api_id, api_hash)

# List of bot usernames and source groups to scan
BOT_USERNAMES = ["RickBurpBot", "PhanesGreenBot", "pocketprotectorbot", "SniperUniversityBot", "thelostsole_bot", "DexTools_Bot"]
SOURCE_GROUPS = [-1001758236818, -1002238854475, -1002179220327, -1002554339683]  # The Sauna, PBC Lounge, Sniper University, PumpFun Unfiltered

async def get_bot_response_for_contract(contract, scan_limit=250):
    """
    Scan messages from known bots to find information about a specific contract address.
    
    Args:
        contract: The contract address to search for
        scan_limit: How many recent messages to scan per group
        
    Returns:
        Dict with token metadata or None if not found
    """
    await client.start()
    print(f"🤖 Scanning bot messages for {contract}")
    
    # First check if any bots have posted about this contract
    for group_id in SOURCE_GROUPS:
        try:
            print(f"🔍 Scanning group {group_id} for contract {contract[:10]}...")
            
            async for message in client.iter_messages(PeerChannel(group_id), limit=scan_limit):
                if not message.text:
                    continue
                    
                # Make sure it's from a bot we recognize
                if not hasattr(message.sender, 'username') or message.sender.username not in BOT_USERNAMES:
                    continue

                # Check if this message contains our contract
                if contract not in message.text:
                    continue
                    
                print(f"✅ Found message from {message.sender.username} about {contract[:10]}...")
                
                # Parse Symbol (e.g., **$AGI**)
                symbol_match = re.search(r"\*\*\$(\w+)\*\*", message.text)
                symbol = symbol_match.group(1) if symbol_match else "UNKNOWN"

                # Parse Market Cap (e.g., MC: **$315.4K**)
                mc_match = re.search(r"MC[:\s]*\*\*\$([\d\.]+[KMB]?)\*\*", message.text)
                market_cap = parse_number(mc_match.group(1)) if mc_match else 0

                # Parse Volume (e.g., Vol: **$4.84M**)
                vol_match = re.search(r"Vol[:\s]*\*\*\$([\d\.]+[KMB]?)\*\*", message.text)
                volume = parse_number(vol_match.group(1)) if vol_match else 0

                # Parse ATH (e.g., ATH: **$950.5K**)
                ath_match = re.search(r"ATH[:\s]*\*\*\$([\d\.]+[KMB]?)\*\*", message.text)
                ath = parse_number(ath_match.group(1)) if ath_match else market_cap

                # Parse Twitter link
                twitter_match = re.search(r"\[𝕏\]\((https:\/\/[^\)]+)\)", message.text)
                if not twitter_match:
                    twitter_match = re.search(r"\[Twitter\]\((https:\/\/[^\)]+)\)", message.text)
                twitter = twitter_match.group(1) if twitter_match else None
                
                # Parse website link (e.g. [Website](https://website.com))
                website_match = re.search(r"\[Website\]\((https?:\/\/[^\)]+)\)", message.text)
                website = website_match.group(1) if website_match else None
                
                # Parse price (e.g., Price: **$0.000006**)
                price_match = re.search(r"Price[:\s]*\*\*\$([\d\.]+)\*\*", message.text)
                price_usd = float(price_match.group(1)) if price_match else 0
                
                # Parse holders (e.g., Holders: **142**)
                holders_match = re.search(r"Holders[:\s]*\*\*(\d+)\*\*", message.text)
                holders = int(holders_match.group(1)) if holders_match else 0
                
                # Try to extract name/title if available
                name_match = re.search(r"# ([\w\s]+)\n", message.text)
                name = name_match.group(1).strip() if name_match else symbol
                
                # Parse liquidity
                liq_match = re.search(r"Liq[^:]*[:\s]*\*\*\$([\d\.]+[KMB]?)\*\*", message.text)
                liquidity = parse_number(liq_match.group(1)) if liq_match else 0

                # Prepare token metadata for Firestore
                metadata = {
                    "symbol": symbol,
                    "token": symbol,
                    "contract": contract,
                    "marketCap": market_cap,
                    "volume24h": volume,
                    "priceUsd": price_usd,
                    "athMarketCap": market_cap,  # Set initial ATH to current market cap
                    "timestamp": firestore.SERVER_TIMESTAMP,
                    "dexUrl": f"https://dexscreener.com/solana/{contract}",
                    "status": "LIVE",
                    "updated": firestore.SERVER_TIMESTAMP,
                    "chain": "solana",
                    "socials": {
                        "twitter": twitter or ""
                    }
                }
                
                # Only set initialMarketCap when creating a new token, 
                # this avoids overwriting existing values during updates
                token_doc = db.collection("calls").where("contract", "==", contract).limit(1).get()
                if not list(token_doc):  # Only set initialMarketCap for new tokens
                    metadata["initialMarketCap"] = market_cap

                print(f"✅ Parsed from bot {message.sender.username}: {metadata['symbol']} with MC=${metadata['marketCap']}")
                return metadata
                
        except Exception as e:
            print(f"❌ Error scanning group {group_id}: {e}")
    
    # Next, scan for any message containing the contract, even if not from a bot
    # This helps find cases where a contract was mentioned but not in a bot message
    print(f"🔍 Scanning for any mentions of contract {contract[:10]} in recent messages...")
    
    for group_id in SOURCE_GROUPS:
        try:
            async for message in client.iter_messages(PeerChannel(group_id), limit=30):
                if not message.text:
                    continue
                    
                if contract in message.text:
                    print(f"✅ Found mention of contract in message from: {getattr(message.sender, 'username', 'unknown')}")
                    
                    # Extract any tokens/symbols from the message using common patterns
                    symbol_matches = re.findall(r"\$(\w+)", message.text)
                    if symbol_matches:
                        symbol = symbol_matches[0].upper()
                        print(f"✅ Extracted potential symbol: {symbol}")
                        
                        # Create basic metadata based on mention
                        metadata = {
                            "symbol": symbol,
                            "name": symbol,
                            "contract": contract,
                            "marketCap": 100000,  # Default placeholder
                            "volume24h": 5000,    # Default placeholder
                            "dexUrl": f"https://dexscreener.com/solana/{contract}",
                            "source": "message-mention",
                            "timestamp": firestore.SERVER_TIMESTAMP,
                            "updated": firestore.SERVER_TIMESTAMP,
                            "lastRefreshed": firestore.SERVER_TIMESTAMP,
                            "initialMarketCap": 100000,
                            "athMarketCap": 100000,
                            "status": "LIVE",
                            "chain": "solana",
                            "socials": {
                                "twitter": ""
                            }
                        }
                        
                        return metadata
        except Exception as e:
            print(f"❌ Error scanning for mentions in group {group_id}: {e}")

    print(f"❌ No bot message or mention found for {contract}")
    return None

def parse_number(value):
    if not value:
        return 0
        
    value = value.upper().replace(",", "").replace("$", "")
    multiplier = 1
    if "K" in value:
        multiplier = 1_000
        value = value.replace("K", "")
    elif "M" in value:
        multiplier = 1_000_000
        value = value.replace("M", "")
    elif "B" in value:
        multiplier = 1_000_000_000
        value = value.replace("B", "")
    try:
        return int(float(value) * multiplier)
    except:
        return 0

async def scan_history_for_solana_contracts(limit=500):
    """Scan message history in monitored groups for Solana contracts and store them in the cache"""
    await client.start()
    print(f"🔍 Scanning history for Solana contracts (limit: {limit} messages per group)...")
    
    # Solana address pattern - base58 format, usually 32-44 chars
    pattern = r"([1-9A-HJ-NP-Za-km-z]{32,44})"
    
    contracts_found = {}
    
    for group_id in SOURCE_GROUPS:
        group_contracts = 0
        try:
            async for message in client.iter_messages(PeerChannel(group_id), limit=limit):
                if not message.text:
                    continue
                    
                matches = re.findall(pattern, message.text)
                for match in matches:
                    if match not in contracts_found:
                        contracts_found[match] = 1
                        group_contracts += 1
                    else:
                        contracts_found[match] += 1
            
            print(f"✅ Found {group_contracts} unique contracts in group {group_id}")
        except Exception as e:
            print(f"❌ Error scanning group {group_id}: {e}")
    
    print(f"🔍 Total unique contracts found: {len(contracts_found)}")
    
    # Return the contracts ordered by frequency (most mentioned first)
    sorted_contracts = sorted(contracts_found.items(), key=lambda x: x[1], reverse=True)
    return [contract for contract, count in sorted_contracts]

if __name__ == "__main__":
    contract = "GN2G7d2qWfsfG3j6CXsiHuuTN5Huzkq4dq86Y4o7yiKc"
    asyncio.run(get_bot_response_for_contract(contract))

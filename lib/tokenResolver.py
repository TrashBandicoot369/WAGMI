import aiohttp
import asyncio
from google.cloud import firestore
from lib.firebase_admin_setup import db

token_cache = db.collection("tokenCache")
memory_token_cache = {}

BIRDEYE_API_KEY = "dd933b6e1c864e618a80c0f554bd819f"

async def fetch_json(session, url, headers=None):
    try:
        async with session.get(url, headers=headers, timeout=10) as res:
            if res.status == 200:
                return await res.json()
            else:
                print(f"⚠️ API status: {res.status} for {url}")
    except Exception as e:
        print(f"❌ Fetch error: {e}")
    return None

async def fetch_birdeye_metadata(contract):
    url = f"https://public-api.birdeye.so/public/token/{contract}"
    headers = {"X-API-KEY": BIRDEYE_API_KEY}

    async with aiohttp.ClientSession() as session:
        data = await fetch_json(session, url, headers)
        if not data or "data" not in data:
            print(f"❌ Birdeye: No data for {contract}")
            return None

        token_data = data["data"]
        symbol = token_data.get("symbol")
        market_cap = token_data.get("market_cap", 0)

        if not symbol or market_cap <= 0:
            print(f"⚠️ Birdeye: Invalid data for {contract}")
            return None

        metadata = {
            "symbol": symbol,
            "contract": contract,
            "marketCap": market_cap,
            "volume24h": token_data.get("volume_24h", 0),
            "priceUsd": token_data.get("price", 0),
            "dexUrl": f"https://birdeye.so/token/{contract}",
            "source": "birdeye",
            "timestamp": firestore.SERVER_TIMESTAMP,
            "athMarketCap": market_cap,
            "twitter": token_data.get("twitter"),
            "website": token_data.get("website")
        }

        print(f"✅ Birdeye resolved {symbol}: MC=${market_cap}")
        return metadata

async def resolve_token_metadata(contract: str, db_instance=None, retries: int = 1, delay: int = 3) -> dict:
    if contract in memory_token_cache and "marketCap" in memory_token_cache[contract]:
        print(f"✅ [Memory Cache] {memory_token_cache[contract]['symbol']}")
        return memory_token_cache[contract]

    cache_ref = db_instance.collection("tokenCache") if db_instance else token_cache
    cached = cache_ref.document(contract).get()
    if cached.exists:
        cache_data = cached.to_dict()
        if "marketCap" in cache_data and cache_data.get("marketCap") != 0:
            print(f"✅ [Cache] {cache_data['symbol']}")
            memory_token_cache[contract] = cache_data
            return cache_data

    async with aiohttp.ClientSession() as session:
        for attempt in range(retries):
            print(f"🔍 Dexscreener Attempt {attempt + 1} for {contract}")
            url = f"https://api.dexscreener.com/latest/dex/pairs/solana/{contract}"
            data = await fetch_json(session, url)

            if data and "pairs" in data and data["pairs"]:
                pair = data["pairs"][0]
                symbol = pair.get("baseToken", {}).get("symbol")
                market_cap = pair.get("fdv", 0)

                if symbol and symbol.upper() != "UNKNOWN" and market_cap > 0:
                    metadata = {
                        "symbol": symbol,
                        "contract": contract,
                        "marketCap": market_cap,
                        "volume24h": pair.get("volume", {}).get("h24", 0),
                        "priceUsd": pair.get("priceUsd", 0),
                        "dexUrl": f"https://dexscreener.com/solana/{contract}",
                        "source": "dexscreener",
                        "timestamp": firestore.SERVER_TIMESTAMP,
                        "athMarketCap": market_cap
                    }
                    print(f"✅ Dexscreener resolved {symbol}: MC=${market_cap}")
                    cache_ref.document(contract).set(metadata)
                    memory_token_cache[contract] = metadata
                    return metadata

            await asyncio.sleep(delay)

    print(f"⚡ Falling back to Birdeye for {contract}")
    metadata = await fetch_birdeye_metadata(contract)
    if metadata:
        cache_ref.document(contract).set(metadata)
        memory_token_cache[contract] = metadata
        return metadata

    print(f"❌ Could not resolve {contract} via Dexscreener or Birdeye")
    return None

async def retry_unknown_tokens(db_instance, max_tokens=10):
    """Retry resolution for tokens that failed to resolve previously"""
    print(f"🔄 Running retry for up to {max_tokens} unknown tokens")
    
    # Query for unknown tokens in the calls collection where symbol is UNKNOWN
    unknown_tokens_query = db_instance.collection("calls").where("symbol", "==", "UNKNOWN").limit(max_tokens)
    unknown_docs = unknown_tokens_query.stream()
    
    retry_count = 0
    success_count = 0
    
    for doc in unknown_docs:
        token_data = doc.to_dict()
        contract = token_data.get("contract")
        
        if not contract:
            continue
            
        print(f"🔄 Retrying token resolution for {contract}")
        retry_count += 1
        
        # Try to resolve token with higher retry count
        token_metadata = await resolve_token_metadata(contract, db_instance, retries=3, delay=2)
        
        if token_metadata and token_metadata.get("symbol", "UNKNOWN") != "UNKNOWN":
            # Update the document with the new metadata
            success_count += 1
            
            # Update only the token metadata fields, preserve the rest
            update_data = {
                "symbol": token_metadata.get("symbol"),
                "token": token_metadata.get("symbol"),  # Keep token field in sync with symbol
                "marketCap": token_metadata.get("marketCap", 0),
                "volume24h": token_metadata.get("volume24h", 0),
                "volume": token_metadata.get("volume24h", 0),
                "lastRefreshed": firestore.SERVER_TIMESTAMP
            }
            
            # Add additional fields if available
            if token_metadata.get("twitter"):
                update_data["twitter"] = token_metadata.get("twitter")
                
                # Update socials object as well
                socials = {}
                socials["twitter"] = token_metadata.get("twitter")
                if token_metadata.get("website"):
                    socials["website"] = token_metadata.get("website")
                    
                update_data["socials"] = socials
            
            # Update the document
            doc.reference.update(update_data)
            print(f"✅ Updated {contract} with symbol {token_metadata.get('symbol')}")
        else:
            # The bot fallback can't be directly implemented here because we need access to:
            # 1. The Telegram client to query bots
            # 2. A message context to reply to
            # Instead, we'll mark that this token needs special handling in the Telegram bot main flow
            print(f"❓ Marking {contract} for bot-based resolution in next message pass")
            
            # Set a flag in the document to indicate it needs bot-based resolution
            doc.reference.update({
                "needs_bot_resolution": True,
                "last_retry_attempt": firestore.SERVER_TIMESTAMP
            })
            
    print(f"🔄 Retry complete: {success_count}/{retry_count} tokens updated successfully")
    return success_count

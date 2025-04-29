import aiohttp
import asyncio
import random
import time
import logging
from firebase_admin import firestore
from firebase_admin_setup import db

# Configure logging
logger = logging.getLogger("token_resolver")

token_cache = db.collection("tokenCache")
memory_token_cache = {}

BIRDEYE_API_KEY = "dd933b6e1c864e618a80c0f554bd819f"

# Add semaphore for preventing concurrent cache writes
cache_semaphore = asyncio.Semaphore(3)  # Allow up to 3 simultaneous cache writes

async def fetch_json(session, url, headers=None):
    try:
        async with session.get(url, headers=headers, timeout=10) as res:
            if res.status == 200:
                return await res.json()
            else:
                logger.warning(f"⚠️ API status: {res.status} for {url}")
    except asyncio.TimeoutError:
        logger.warning(f"⏱️ Timeout fetching {url}")
    except Exception as e:
        logger.error(f"❌ Fetch error: {e}")
    return None

async def fetch_birdeye_metadata(contract):
    url = f"https://public-api.birdeye.so/public/token/{contract}"
    headers = {"X-API-KEY": BIRDEYE_API_KEY}

    logger.info(f"🔍 Fetching Birdeye data for {contract}")
    async with aiohttp.ClientSession() as session:
        data = await fetch_json(session, url, headers)
        if not data or "data" not in data:
            logger.warning(f"❌ Birdeye: No data for {contract}")
            return None

        token_data = data["data"]
        symbol = token_data.get("symbol")
        market_cap = token_data.get("market_cap", 0)

        if not symbol or market_cap <= 0:
            logger.warning(f"⚠️ Birdeye: Invalid data for {contract}")
            return None

        # Standardize fields to match required Firestore structure
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
            # Note: initialMarketCap is intentionally NOT included to avoid overwriting 
            "twitter": token_data.get("twitter"),
            "website": token_data.get("website"),
            "chain": "solana",
            "status": "LIVE",
            "updated": firestore.SERVER_TIMESTAMP,
            "lastRefreshed": firestore.SERVER_TIMESTAMP,
            "name": token_data.get("name", symbol),
            "socials": {
                "twitter": token_data.get("twitter", "")
            }
        }

        logger.info(f"✅ Birdeye resolved {symbol}: MC=${market_cap}")
        return metadata

async def fetch_solscan_metadata(contract):
    """Fetch token data from Solscan API"""
    logger.info(f"🔍 Fetching Solscan data for {contract}")
    try:
        async with aiohttp.ClientSession() as session:
            # Get token metadata
            meta_url = f"https://public-api.solscan.io/token/meta?tokenAddress={contract}"
            meta_data = await fetch_json(session, meta_url)
            
            if not meta_data or not meta_data.get("symbol"):
                logger.warning(f"❌ Solscan: No metadata for {contract}")
                return None
                
            # Get market data
            market_url = f"https://public-api.solscan.io/market/token/{contract}"
            market_data = await fetch_json(session, market_url)
            
            symbol = meta_data.get("symbol", "UNKNOWN")
            price_usd = float(market_data.get("priceUsd", 0)) if market_data else 0
            supply = int(meta_data.get("supply", 0)) / (10 ** int(meta_data.get("decimals", 9)))
            
            # Calculate market cap from price and supply
            market_cap = price_usd * supply if price_usd and supply else 0
            
            if market_cap <= 0:
                logger.warning(f"⚠️ Solscan: Could not calculate market cap for {contract}")
                return None
                
            # Get social links
            twitter = None
            website = None
            for link in meta_data.get("links", {}).values():
                if isinstance(link, str):
                    if "twitter.com" in link:
                        twitter = link
                    elif not website and "." in link and not any(x in link for x in ["twitter", "telegram", "discord", "medium"]):
                        website = link
            
            # Standardize fields to match required Firestore structure
            metadata = {
                "symbol": symbol,
                "contract": contract,
                "marketCap": market_cap,
                "volume24h": 0,  # Solscan doesn't provide volume data in their public API
                "priceUsd": price_usd,
                "dexUrl": f"https://solscan.io/token/{contract}",
                "source": "solscan",
                "timestamp": firestore.SERVER_TIMESTAMP,
                "athMarketCap": market_cap,
                # Note: initialMarketCap is intentionally NOT included to avoid overwriting 
                "twitter": twitter,
                "website": website,
                "chain": "solana",
                "status": "LIVE",
                "updated": firestore.SERVER_TIMESTAMP,
                "lastRefreshed": firestore.SERVER_TIMESTAMP,
                "name": meta_data.get("name", symbol),
                "socials": {
                    "twitter": twitter or ""
                }
            }
            
            logger.info(f"✅ Solscan resolved {symbol}: MC=${market_cap}")
            return metadata
    except Exception as e:
        logger.error(f"❌ Solscan error: {e}")
        return None

async def write_to_cache(cache_ref, contract, metadata, max_retries=3):
    """Helper function to write to Firestore with retries and random backoff"""
    retry_count = 0
    
    # Use semaphore to prevent too many concurrent cache writes
    async with cache_semaphore:
        while retry_count < max_retries:
            try:
                # Add a slight randomized delay to avoid write conflicts (50-200ms)
                delay_ms = random.randint(50, 200)
                await asyncio.sleep(delay_ms / 1000)
                
                # Ensure the data conforms to the required structure
                # Add required fields if they are missing
                if "socials" not in metadata and "twitter" in metadata:
                    metadata["socials"] = {"twitter": metadata["twitter"] or ""}
                    
                if "name" not in metadata and "symbol" in metadata:
                    metadata["name"] = metadata["symbol"]
                    
                cache_ref.document(contract).set(metadata)
                logger.info(f"✅ Cache updated for {metadata.get('symbol', 'UNKNOWN')}")
                memory_token_cache[contract] = metadata
                return True
            except Exception as e:
                retry_count += 1
                # Use exponential backoff with jitter for retries
                backoff = (2 ** retry_count) + random.uniform(0, 0.5)
                logger.warning(f"⚠️ Cache write failed (attempt {retry_count}/{max_retries}): {e}")
                logger.info(f"   Retrying in {backoff:.2f}s...")
                await asyncio.sleep(backoff)
    
    logger.error(f"❌ Failed to update cache after {max_retries} attempts for {contract}")
    return False

async def resolve_token_metadata(contract: str, db_instance=None, retries: int = 2, delay: int = 3) -> dict:
    """
    Resolve token metadata from various sources with improved caching and fallback mechanisms.
    
    Args:
        contract: The contract address to resolve
        db_instance: Firestore database instance (optional)
        retries: Number of retries for API calls
        delay: Delay between retries
        
    Returns:
        Dictionary with token metadata or None if resolution fails
    """
    # Track resolution start time
    start_time = time.time()
    logger.info(f"🔍 Starting token metadata resolution for {contract}")
    
    # Check memory cache first for fastest response
    if contract in memory_token_cache and "marketCap" in memory_token_cache[contract]:
        cached_data = memory_token_cache[contract]
        # Only return from memory cache if it's valid data
        if cached_data.get("marketCap", 0) > 0 and cached_data.get("symbol", "UNKNOWN") != "UNKNOWN":
            logger.info(f"✅ [Memory Cache] {cached_data['symbol']}")
            
            # Ensure the data structure conforms to requirements
            if "socials" not in cached_data and "twitter" in cached_data:
                cached_data["socials"] = {"twitter": cached_data["twitter"] or ""}
                
            return cached_data
        else:
            logger.warning(f"⚠️ [Memory Cache] Invalid data for {contract}, continuing resolution")

    cache_ref = db_instance.collection("tokenCache") if db_instance else token_cache
    
    # Check Firestore cache next
    try:
        cached = cache_ref.document(contract).get()
        if cached.exists:
            cache_data = cached.to_dict()
            # Only use cache data if it has valid market cap and symbol
            if "marketCap" in cache_data and cache_data.get("marketCap") > 0 and cache_data.get("symbol") != "UNKNOWN":
                # Update timestamp to indicate this was recently accessed
                cache_data["updated"] = firestore.SERVER_TIMESTAMP
                
                # Ensure the data structure conforms to requirements
                if "socials" not in cache_data and "twitter" in cache_data:
                    cache_data["socials"] = {"twitter": cache_data["twitter"] or ""}
                
                # Update cache asynchrously to avoid blocking the main resolution flow
                asyncio.create_task(write_to_cache(cache_ref, contract, cache_data))
                
                logger.info(f"✅ [Cache] {cache_data['symbol']} with MC=${cache_data.get('marketCap', 0)}")
                memory_token_cache[contract] = cache_data
                return cache_data
    except Exception as e:
        logger.warning(f"⚠️ Cache read error: {e}")
        # Continue to resolution if cache read fails

    # Try DexScreener first - most reliable source
    logger.info(f"🔍 Starting API resolution for {contract}")
    async with aiohttp.ClientSession() as session:
        for attempt in range(retries):
            logger.info(f"🔍 Dexscreener Attempt {attempt + 1} for {contract}")
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
                        "athMarketCap": market_cap,
                        # Note: initialMarketCap is intentionally NOT included to avoid overwriting 
                        "chain": "solana",
                        "status": "LIVE",
                        "updated": firestore.SERVER_TIMESTAMP,
                        "lastRefreshed": firestore.SERVER_TIMESTAMP,
                        "name": pair.get("baseToken", {}).get("name", symbol),
                        "socials": {
                            "twitter": ""  # DexScreener doesn't provide social links in API
                        }
                    }
                    logger.info(f"✅ Dexscreener resolved {symbol}: MC=${market_cap}")
                    
                    # Write to cache with retries and backoff
                    await write_to_cache(cache_ref, contract, metadata)
                    return metadata

            # Add jitter to the retry delay (±50%)
            jitter = delay * random.uniform(0.5, 1.5)
            await asyncio.sleep(jitter)

    # Try Birdeye if DexScreener failed
    logger.info(f"⚡ Falling back to Birdeye for {contract}")
    birdeye_metadata = await fetch_birdeye_metadata(contract)
    if birdeye_metadata:
        await write_to_cache(cache_ref, contract, birdeye_metadata)
        return birdeye_metadata
        
    # Try Solscan if Birdeye failed
    logger.info(f"⚡ Falling back to Solscan for {contract}")
    solscan_metadata = await fetch_solscan_metadata(contract)
    if solscan_metadata:
        await write_to_cache(cache_ref, contract, solscan_metadata)
        return solscan_metadata

    # Remove Telegram bot resolution since that's now handled in qwant3.py directly
    # We'll return None to indicate that API resolution failed and the caller should try bot resolution
    logger.warning(f"❌ All API resolution methods failed for {contract} - caller should try bot resolution")
    
    # Log total resolution time for analytics
    resolution_time = time.time() - start_time
    logger.info(f"⏱️ API resolution completed in {resolution_time:.2f}s without success")
    
    return None


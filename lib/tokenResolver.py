import aiohttp
import asyncio
from google.cloud import firestore

# Firebase collection
token_cache = db.collection("tokenCache")

async def fetch_json(session, url):
    try:
        async with session.get(url, timeout=10) as res:
            if res.status == 200:
                return await res.json()
            else:
                print(f"⚠️ Dexscreener status: {res.status}")
    except Exception as e:
        print(f"❌ Fetch error: {e}")
    return None

async def resolve_token_symbol(contract: str, retries: int = 5, delay: int = 5) -> str:
    # Check Firestore cache
    cached = token_cache.document(contract).get()
    if cached.exists:
        symbol = cached.to_dict().get("symbol", "UNKNOWN")
        if symbol != "UNKNOWN":
            print(f"✅ [Cache] Token found: {symbol}")
            return symbol

    async with aiohttp.ClientSession() as session:
        for attempt in range(retries):
            print(f"🔍 [Dexscreener] Attempt {attempt + 1} for {contract}...")
            url = f"https://api.dexscreener.com/latest/dex/pairs/solana/{contract}"
            data = await fetch_json(session, url)

            if data and "pairs" in data and data["pairs"]:
                symbol = data["pairs"][0].get("baseToken", {}).get("symbol", "UNKNOWN")
                if symbol != "UNKNOWN":
                    print(f"✅ Token found: {symbol}")
                    token_cache.document(contract).set({
                        "symbol": symbol,
                        "source": "dexscreener",
                        "timestamp": firestore.SERVER_TIMESTAMP,
                    })
                    return symbol

            await asyncio.sleep(delay * (attempt + 1))  # exponential backoff

    print("❌ Token not found after retries. Setting as UNKNOWN.")
    token_cache.document(contract).set({
        "symbol": "UNKNOWN",
        "source": "dexscreener",
        "timestamp": firestore.SERVER_TIMESTAMP,
    })
    return "UNKNOWN"

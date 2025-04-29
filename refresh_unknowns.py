import asyncio
from lib.firebase_admin_setup import db
from lib.tokenResolver import resolve_token_metadata
from firebase_admin import firestore

calls_ref = db.collection("calls")

async def refresh_unknown_tokens():
    print("🔍 Finding UNKNOWN tokens in database...")

    unknown_calls = calls_ref.where("symbol", "==", "UNKNOWN").get()
    print(f"Found {len(unknown_calls)} calls with UNKNOWN tokens")

    updated_count = 0
    still_unknown = 0

    for doc in unknown_calls:
        data = doc.to_dict()
        dex_url = data.get("dexUrl") or data.get("dexurl")

        if not dex_url:
            print(f"⚠️ Missing dexUrl for doc {doc.id}, skipping")
            continue

        contract = dex_url.split("/")[-1]
        if not contract:
            print(f"⚠️ Could not extract contract from {dex_url}, skipping")
            continue

        print(f"🔄 Refreshing token data for contract: {contract}")
        token_metadata = await resolve_token_metadata(contract, db, retries=3)

        if not token_metadata or token_metadata.get("symbol", "UNKNOWN") == "UNKNOWN":
            print(f"❌ Still couldn't resolve token for {contract}")
            still_unknown += 1
            continue

        symbol = token_metadata.get("symbol")
        market_cap = token_metadata.get("marketCap", 0)
        volume_24h = token_metadata.get("volume24h", 0)

        # Preserve existing ATH and initial market cap
        initial_cap = data.get("initialMarketCap", 0)
        
        # Only set initial cap if it doesn't exist
        if initial_cap <= 0:
            initial_cap = market_cap
            print(f"📊 Setting initial market cap for new token {symbol}: ${market_cap}")
        
        ath_cap = max(data.get("athMarketCap", 0), market_cap)

        update_data = {
            "symbol": symbol,
            "token": symbol,
            "contract": contract,
            "dexUrl": f"https://dexscreener.com/solana/{contract}",
            "marketCap": market_cap,
            "volume24h": volume_24h,
            "volume": volume_24h,
            "initialMarketCap": initial_cap,
            "athMarketCap": ath_cap,
            "percentChange24h": 0,
            "capChange": 0,
            "lastRefreshed": firestore.SERVER_TIMESTAMP,
            "updated": firestore.SERVER_TIMESTAMP
        }

        # Add Twitter handle if available
        update_data["twitter"] = token_metadata.get("twitter", None)

        # Add socials if available
        socials = {}
        if token_metadata.get("twitter"):
            socials["twitter"] = token_metadata.get("twitter")
        if token_metadata.get("website"):
            socials["website"] = token_metadata.get("website")
        if socials:
            update_data["socials"] = socials

        # Preserve shotCaller and original timestamp
        if "shotCaller" in data:
            update_data["shotCaller"] = data.get("shotCaller", False)
        if "timestamp" in data:
            update_data["timestamp"] = data.get("timestamp")

        doc.reference.update(update_data)
        print(f"✅ Updated {symbol}: MC=${market_cap}, Vol=${volume_24h}")
        updated_count += 1

        await asyncio.sleep(1)

    print(f"✅ Complete! Updated {updated_count} tokens. {still_unknown} still unresolved.")
    return updated_count, still_unknown

if __name__ == "__main__":
    print("🚀 Starting unknown token refresh...")
    asyncio.run(refresh_unknown_tokens())
    print("✅ Done!")

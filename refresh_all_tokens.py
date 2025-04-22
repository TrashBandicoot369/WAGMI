import asyncio
import aiohttp
from lib.firebase_admin_setup import db
from lib.tokenResolver import resolve_token_metadata
from google.cloud import firestore

# Use the db from firebase_admin_setup
calls_ref = db.collection("calls")

async def refresh_all_tokens(limit=20):
    print(f"🔍 Processing up to {limit} most recent tokens...")
    # Get the most recent tokens first
    docs = calls_ref.order_by("timestamp", direction=firestore.Query.DESCENDING).limit(limit).stream()

    count = 0
    for doc in docs:
        count += 1
        data = doc.to_dict()
        contract = data.get("contract", "")

        if not contract:
            # Try to extract contract from dexUrl if available
            dexurl = data.get("dexurl", data.get("dexUrl", ""))
            if dexurl:
                parts = dexurl.split("/")
                if len(parts) > 0:
                    contract = parts[-1]

        if not contract:
            print(f"⚠️ Missing contract address for doc: {doc.id}")
            continue

        print(f"🔄 Processing token {data.get('symbol', 'UNKNOWN')} ({contract})")

        # Get full token metadata from Dexscreener
        token_metadata = await resolve_token_metadata(contract, db)

        if not token_metadata:
            print(f"🚫 Skipping {contract} — could not resolve")
            continue

        # Safe parsing of market caps ensuring we have valid numbers
        def parse_market_cap(value):
            if value is None or value == "UNKNOWN":
                return 0
            try:
                if isinstance(value, str):
                    return float(value)
                return float(value)
            except (ValueError, TypeError):
                print(f"⚠️ Could not parse market cap value: {value}")
                return 0

        # Calculate cap change percentage using safe parsing
        try:
            old_cap = parse_market_cap(data.get("marketCap"))
            new_cap = parse_market_cap(token_metadata.get("marketCap"))
            cap_change = round(((new_cap - old_cap) / old_cap) * 100, 2) if old_cap > 0 else None
        except Exception as e:
            print(f"⚠️ Error calculating cap change: {e}")
            cap_change = None

        # Preserve existing timestamp and shotCaller
        original_timestamp = data.get("timestamp")
        shot_caller = data.get("shotCaller", False)
        
        # Handle initialMarketCap - parse safely
        initial_market_cap = parse_market_cap(data.get("initialMarketCap"))
        if initial_market_cap <= 0 and old_cap > 0:
            initial_market_cap = old_cap
            print(f"📊 Setting initial market cap: ${initial_market_cap:,.2f}")
        
        # Handle athMarketCap - parse safely
        current_ath_cap = parse_market_cap(data.get("athMarketCap"))
        
        # Check if current market cap is higher than stored ATH
        ath_updated = False
        if new_cap > 0:  # Ensure new cap is valid
            if current_ath_cap <= 0 or new_cap > current_ath_cap:
                current_ath_cap = new_cap
                ath_updated = True
                print(f"📈 New ATH for {data.get('symbol', 'UNKNOWN')}: ${new_cap:,.2f}")

        update_data = {
            "contract": contract,
            "symbol": token_metadata.get("symbol", "UNKNOWN"),
            "marketCap": new_cap,
            "volume24h": token_metadata.get("volume24h", "UNKNOWN"),
            "twitter": token_metadata.get("twitter"),
            "dexUrl": token_metadata.get("dexUrl", f"https://dexscreener.com/search?q={contract}"),
            "updated": firestore.SERVER_TIMESTAMP,
            "capChange": cap_change,
            "shotCaller": shot_caller,
        }
        
        # Only add initialMarketCap if we have a valid value
        if initial_market_cap > 0:
            update_data["initialMarketCap"] = initial_market_cap
            
        # Only add athMarketCap if we have a valid value
        if current_ath_cap > 0:
            update_data["athMarketCap"] = current_ath_cap

        if original_timestamp:
            update_data["timestamp"] = original_timestamp

        # Debug information before update
        print(f"DEBUG: Token {data.get('symbol')} before update:")
        print(f"  - MarketCap: Old=${old_cap:,.2f}, New=${new_cap:,.2f}")
        print(f"  - InitialMarketCap: ${initial_market_cap:,.2f}")
        print(f"  - ATH MarketCap: ${current_ath_cap:,.2f}, Updated: {ath_updated}")

        calls_ref.document(doc.id).set(update_data, merge=True)
        status = f"cap change: {cap_change}%"
        if ath_updated:
            status += f", new ATH: ${current_ath_cap:,.2f}"
        print(f"✅ Updated {token_metadata.get('symbol')} — {status}")

    print(f"🏁 Done. {count} tokens processed.")

if __name__ == "__main__":
    asyncio.run(refresh_all_tokens(20))  # Process up to 20 tokens

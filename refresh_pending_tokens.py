import asyncio
from lib.firebase_admin_setup import db
from firebase_admin import firestore
from lib.tokenResolver import resolve_token_metadata

async def refresh_all_tokens(limit: int = 20):
    print("✅ Firebase Admin SDK initialized successfully")

    calls_ref = db.collection("calls").order_by("timestamp", direction=firestore.Query.DESCENDING).limit(limit)
    docs = calls_ref.stream()

    print(f"🔍 Processing up to {limit} most recent tokens...")

    for doc in docs:
        data = doc.to_dict()
        contract = data.get("contract") or data.get("contractAddress")
        if not contract:
            continue

        print(f"🔄 Processing token {data.get('symbol')} ({contract})")

        token_metadata = await resolve_token_metadata(contract, db)

        if not token_metadata:
            print(f"⚠️ No pairs found. Skipping {contract}")
            continue

        # Preserve original initialMarketCap and timestamp
        original_timestamp = data.get("timestamp")
        original_initial_mcap = data.get("initialMarketCap")

        # Calculate cap change
        old_cap = float(data.get("marketCap", 0) or 0)
        new_cap = float(token_metadata.get("marketCap", 0) or 0)
        cap_change = round(((new_cap - old_cap) / old_cap) * 100, 2) if old_cap > 0 else None

        # Create update data with only the fields that should be updated
        update_data = {
            "symbol": token_metadata.get("symbol"),
            "marketCap": new_cap,
            "volume24h": token_metadata.get("volume24h", 0),
            "capChange": cap_change,
            "athMarketCap": max(token_metadata.get("marketCap", 0), data.get("athMarketCap", 0) or 0),
            "lastRefreshed": firestore.SERVER_TIMESTAMP,
            "updated": firestore.SERVER_TIMESTAMP
        }
        
        # Only update social info if we have it
        if token_metadata.get("twitter"):
            update_data["twitter"] = token_metadata.get("twitter")
        if token_metadata.get("socials"):
            update_data["socials"] = token_metadata.get("socials")

        # Set initialMarketCap only if it doesn't exist and preserve timestamp
        if original_initial_mcap:
            update_data["initialMarketCap"] = original_initial_mcap
        elif not original_initial_mcap and new_cap > 0:
            update_data["initialMarketCap"] = new_cap  # Only set if we don't have one
            
        if original_timestamp:
            update_data["timestamp"] = original_timestamp

        db.collection("calls").document(doc.id).set(update_data, merge=True)
        print(f"✅ Updated {data.get('symbol')} with new market cap {cap_change:+.2f}% | Initial MC: ${update_data.get('initialMarketCap', 0):,.2f}")

    print("🏁 Done.")

if __name__ == "__main__":
    asyncio.run(refresh_all_tokens(20))

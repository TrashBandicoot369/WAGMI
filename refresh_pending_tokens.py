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

        # Preserve original timestamp
        original_timestamp = data.get("timestamp")

        # Calculate cap change
        old_cap = float(data.get("marketCap", 0) or 0)
        new_cap = float(token_metadata.get("marketCap", 0) or 0)
        cap_change = round(((new_cap - old_cap) / old_cap) * 100, 2) if old_cap > 0 else None

        updated_data = {
            **data,  # Keep all existing data
            **token_metadata,  # Override with fresh metadata
            "capChange": cap_change,
            "timestamp": original_timestamp  # 🔒 Preserve original timestamp
        }

        db.collection("calls").document(doc.id).set(updated_data, merge=True)
        print(f"✅ Updated {data.get('symbol')} with new market cap +{cap_change}%")

    print("🏁 Done.")

if __name__ == "__main__":
    asyncio.run(refresh_all_tokens(20))

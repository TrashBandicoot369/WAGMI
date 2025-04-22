import asyncio
from lib.firebase_admin_setup import db
from google.cloud import firestore

async def delete_duplicates():
    print("🔍 Scanning Firestore for duplicates...")
    calls_ref = db.collection("calls")
    all_docs = calls_ref.stream()

    symbol_map = {}
    duplicates_to_delete = []

    for doc in all_docs:
        data = doc.to_dict()
        symbol = data.get("symbol", "").upper()

        if not symbol or symbol == "UNKNOWN":
            continue

        ts = data.get("timestamp")
        if symbol not in symbol_map:
            symbol_map[symbol] = (doc.id, ts)
        else:
            existing_id, existing_ts = symbol_map[symbol]

            # Keep the most recent doc, delete the older one
            if ts and existing_ts and ts > existing_ts:
                duplicates_to_delete.append(existing_id)
                symbol_map[symbol] = (doc.id, ts)
            else:
                duplicates_to_delete.append(doc.id)

    print(f"🗑️ Found {len(duplicates_to_delete)} duplicates to delete...")

    for doc_id in duplicates_to_delete:
        db.collection("calls").document(doc_id).delete()
        print(f"✅ Deleted {doc_id}")

    print("🎉 Cleanup complete.")

if __name__ == "__main__":
    asyncio.run(delete_duplicates())

import asyncio
from lib.firebase_admin_setup import db

# Use the db from firebase_admin_setup
token_cache_ref = db.collection("tokenCache")
calls_ref = db.collection("calls")

async def clear_pump_cache():
    print("🔍 Finding cached PUMP tokens...")
    # Get all PUMP tokens in the cache
    pump_docs = list(token_cache_ref.where("symbol", "==", "PUMP").stream())
    print(f"Found {len(pump_docs)} cached PUMP tokens")
    
    # List addresses to delete
    for doc in pump_docs:
        print(f"Will clear: {doc.id}")
    
    # Confirm with user
    confirm = input("Delete these cache entries? (y/n): ")
    if confirm.lower() != 'y':
        print("Aborted. No changes made.")
        return
    
    # Delete all PUMP tokens from cache
    for doc in pump_docs:
        doc.reference.delete()
        print(f"Deleted cache for {doc.id}")
    
    # Mark all calls with PUMP tokens for refresh
    pump_calls = list(calls_ref.where("symbol", "==", "PUMP").stream())
    for doc in pump_calls:
        doc.reference.update({"symbol": "UNKNOWN"})
        print(f"Reset call {doc.id} to UNKNOWN for refresh")
    
    # Also check the old schema
    pump_calls_old = list(calls_ref.where("token", "==", "PUMP").stream())
    for doc in pump_calls_old:
        doc.reference.update({"token": "UNKNOWN"})
        print(f"Reset call {doc.id} to UNKNOWN for refresh (old schema)")
    
    print("✅ Done! Now run refresh_unknowns.py to re-resolve the tokens.")

if __name__ == "__main__":
    asyncio.run(clear_pump_cache()) 
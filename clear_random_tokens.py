import asyncio
from lib.firebase_admin_setup import db

# Use the db from firebase_admin_setup
token_cache_ref = db.collection("tokenCache")
calls_ref = db.collection("calls")

async def clear_long_named_tokens():
    print("🔍 Finding tokens with long random names...")
    
    # Pattern to identify the problematic symbols we created earlier
    bad_symbols = [
        "BTHXQPUJHKHQJIEUEHM",
        "KWCZSPBSHPUMP",
        "ZGPUXMRBBT",
        "SDXUYRQAWLSXLFARMS",
        "AELPIEWAZGUKPES",
        "PYUCMOWUKS",
        "BGDFHTUZBFACWVPUMP",
        "MIYUPHOFEKWFPUMP"
    ]
    
    # Get all problematic tokens
    all_problematic_docs = []
    for symbol in bad_symbols:
        docs = list(token_cache_ref.where("symbol", "==", symbol).stream())
        all_problematic_docs.extend(docs)
    
    print(f"Found {len(all_problematic_docs)} tokens with long random names")
    
    # List contract addresses to clear
    for doc in all_problematic_docs:
        print(f"Will clear cache for: {doc.id} (symbol: {doc.to_dict().get('symbol', 'UNKNOWN')})")
    
    # Confirm with user
    confirm = input("Delete these cache entries? (y/n): ")
    if confirm.lower() != 'y':
        print("Aborted. No changes made.")
        return
    
    # Delete all problematic tokens from cache
    for doc in all_problematic_docs:
        doc.reference.delete()
        print(f"Deleted cache for {doc.id}")
    
    # Find and update all calls with problematic symbols
    for symbol in bad_symbols:
        # New schema
        symbol_calls = list(calls_ref.where("symbol", "==", symbol).stream())
        for doc in symbol_calls:
            doc.reference.update({"symbol": "UNKNOWN"})
            print(f"Reset call {doc.id} to UNKNOWN for refresh")
        
        # Old schema
        token_calls = list(calls_ref.where("token", "==", symbol).stream())
        for doc in token_calls:
            doc.reference.update({"token": "UNKNOWN"})
            print(f"Reset call {doc.id} to UNKNOWN for refresh (old schema)")
    
    print("✅ Done! Now run refresh_unknowns.py to re-resolve the tokens.")

if __name__ == "__main__":
    asyncio.run(clear_long_named_tokens()) 
import asyncio
import aiohttp
from lib.firebase_admin_setup import db
from lib.tokenResolver import resolve_token_metadata
from google.cloud import firestore

# Use the db from firebase_admin_setup
calls_ref = db.collection("calls")

async def refresh_unknowns():
    print("🔍 Searching for 'UNKNOWN' tokens...")
    # Search for documents with unknown symbols
    docs = list(calls_ref.where("symbol", "==", "UNKNOWN").stream())
    print(f"Found {len(docs)} documents with unknown tokens")
    
    for doc in docs:
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
            
        print(f"🔄 Refreshing token for: {contract}")
        
        # Get complete token metadata
        token_metadata = await resolve_token_metadata(contract, db)
        
        # Create update data from token metadata
        update_data = {
            "contract": contract,
            "symbol": token_metadata.get("symbol", "UNKNOWN"),
            "marketCap": token_metadata.get("marketCap", "UNKNOWN"),
            "volume24h": token_metadata.get("volume24h", "UNKNOWN"),
            "twitter": token_metadata.get("twitter"),
            "dexUrl": token_metadata.get("dexUrl", f"https://dexscreener.com/search?q={contract}"),
            "updated": firestore.SERVER_TIMESTAMP
        }
            
        # Update the document
        calls_ref.document(doc.id).update(update_data)
        print(f"✅ Updated {doc.id} with {token_metadata.get('symbol')} metadata")

if __name__ == "__main__":
    asyncio.run(refresh_unknowns())

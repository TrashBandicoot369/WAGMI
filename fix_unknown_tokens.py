import asyncio
import firebase_admin
from lib.firebase_admin_setup import db
from firebase_admin import firestore

# Use the db from firebase_admin_setup
calls_ref = db.collection("calls")

async def fix_unknown_tokens():
    """
    Find tokens marked as UNKNOWN and ensure they have contract field set.
    This extracts the contract address from the dexUrl field.
    """
    print("🔍 Finding UNKNOWN tokens in database...")
    
    # Query all calls with UNKNOWN tokens
    query = calls_ref.where("symbol", "==", "UNKNOWN")
    unknown_calls = query.get()
    
    print(f"Found {len(unknown_calls)} calls with UNKNOWN tokens")
    
    updated_count = 0
    error_count = 0
    
    for doc in unknown_calls:
        # Get the original data
        data = doc.to_dict()
        
        # Check if contract field is already set
        if "contract" in data and data["contract"]:
            print(f"✅ Document {doc.id} already has contract field, skipping")
            continue
            
        # Extract contract address from dexUrl
        dex_url = data.get("dexUrl") or data.get("dexurl")
        if not dex_url:
            print(f"⚠️ Missing dexUrl for doc {doc.id}, skipping")
            error_count += 1
            continue
            
        # Extract contract from URL
        try:
            contract = dex_url.split("/")[-1]
        except:
            print(f"⚠️ Invalid dexUrl format: {dex_url}")
            error_count += 1
            continue
            
        if not contract:
            print(f"⚠️ Could not extract contract from {dex_url}")
            error_count += 1
            continue
            
        print(f"🔄 Adding contract field for {doc.id}: {contract}")
        
        # Add contract field to document
        update_data = {
            "contract": contract,
            "updated": firestore.SERVER_TIMESTAMP
        }
        
        # Update the document
        doc.reference.update(update_data)
        print(f"✅ Updated document {doc.id} with contract: {contract}")
        updated_count += 1
        
    print(f"✅ Complete! Added contract field to {updated_count} tokens. Errors: {error_count}")
    return updated_count, error_count

if __name__ == "__main__":
    print("🚀 Starting unknown token fix...")
    asyncio.run(fix_unknown_tokens())
    print("✅ Done!") 
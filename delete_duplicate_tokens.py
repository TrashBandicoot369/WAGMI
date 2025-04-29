import asyncio
from lib.firebase_admin_setup import db
from google.cloud import firestore

# Use the db from firebase_admin_setup
calls_ref = db.collection("calls")

async def delete_duplicate_tokens(dry_run=True):
    print(f"🔍 Scanning for duplicates (Dry run: {dry_run})...")
    
    # Get all tokens
    docs = calls_ref.stream()
    
    # Create a dictionary to track tokens by contract address
    tokens_by_contract = {}
    
    # Track count of documents
    total_count = 0
    
    # First pass - collect all tokens and identify duplicates
    for doc in docs:
        total_count += 1
        data = doc.to_dict()
        
        # Extract contract from document
        contract = data.get("contract", "")
        
        # If contract is missing, try to extract from dexUrl
        if not contract:
            dexurl = data.get("dexurl", data.get("dexUrl", ""))
            if dexurl:
                parts = dexurl.split("/")
                if len(parts) > 0:
                    contract = parts[-1]
        
        # Skip if we couldn't identify a contract
        if not contract:
            print(f"⚠️ Skipping doc {doc.id} - No contract address found")
            continue
            
        # Extract timestamp for sorting
        timestamp = data.get("timestamp", None)
        if not timestamp:
            # If no timestamp, use updated field or set to now
            timestamp = data.get("updated", firestore.SERVER_TIMESTAMP)
            
        # If this is a new contract, initialize its entry
        if contract not in tokens_by_contract:
            tokens_by_contract[contract] = []
            
        # Add this document to the contract's list
        tokens_by_contract[contract].append({
            "doc_id": doc.id,
            "timestamp": timestamp,
            "symbol": data.get("symbol", data.get("token", "UNKNOWN")),
            "marketCap": data.get("marketCap", 0)
        })
    
    # Count duplicates
    duplicates_count = 0
    tokens_to_delete = []
    
    # Second pass - identify which documents to keep/delete
    for contract, docs in tokens_by_contract.items():
        if len(docs) > 1:
            # Sort by timestamp (oldest first)
            sorted_docs = sorted(docs, key=lambda x: x["timestamp"])
            
            # Keep the oldest document, mark others for deletion
            kept_doc = sorted_docs[0]
            for doc in sorted_docs[1:]:
                duplicates_count += 1
                tokens_to_delete.append({
                    "doc_id": doc["doc_id"],
                    "symbol": doc["symbol"],
                    "contract": contract
                })
                
            print(f"📋 Contract {contract} ({kept_doc['symbol']}) - Found {len(docs)} duplicates, keeping doc {kept_doc['doc_id']}")
    
    # Summary before deletion
    print(f"\n📊 Summary:")
    print(f"   Total documents: {total_count}")
    print(f"   Unique contracts: {len(tokens_by_contract)}")
    print(f"   Duplicates found: {duplicates_count}")
    
    # Delete duplicates if not in dry run
    if not dry_run and tokens_to_delete:
        print("\n⚠️ DELETING DUPLICATES...")
        for doc in tokens_to_delete:
            print(f"🗑️ Deleting {doc['symbol']} ({doc['contract']}) - Doc ID: {doc['doc_id']}")
            calls_ref.document(doc["doc_id"]).delete()
        print(f"✅ Deleted {len(tokens_to_delete)} duplicate documents")
    elif tokens_to_delete:
        print("\n🛑 DRY RUN - No documents were deleted")
        print(f"   Would have deleted {len(tokens_to_delete)} documents")
        print("\nTo delete these documents, run again with dry_run=False")
    else:
        print("\n✅ No duplicates found!")

if __name__ == "__main__":
    # By default, run in dry run mode (no actual deletions)
    # Change to False to actually delete the duplicates
    asyncio.run(delete_duplicate_tokens(dry_run=False))

import asyncio
import sys
from lib.firebase_admin_setup import db
from firebase_admin import firestore
import time

# Define the collections to clear
COLLECTIONS = {
    "calls": "calls",
    "pending": "pendingTokens",
    "cache": "tokenCache"
}

async def delete_collection(collection_name, batch_size=500):
    """
    Delete all documents in a collection in batches to avoid timeout
    """
    coll_ref = db.collection(collection_name)
    docs = coll_ref.limit(batch_size).stream()
    deleted = 0
    
    # Convert to list to get count
    doc_list = list(docs)
    total = len(doc_list)
    
    if total == 0:
        print(f"Collection '{collection_name}' is already empty.")
        return 0

    print(f"Deleting {total} documents from '{collection_name}'...")
    
    # Delete documents in batches
    for doc in doc_list:
        doc.reference.delete()
        deleted += 1
        # Show progress
        if deleted % 100 == 0:
            print(f"Deleted {deleted}/{total} documents...")
    
    print(f"✅ Successfully deleted {deleted} documents from '{collection_name}'")
    return deleted

async def clear_collections(collections_to_clear):
    """
    Clear specified collections
    """
    if not collections_to_clear:
        print("No collections specified to clear.")
        return

    total_deleted = 0
    
    for coll in collections_to_clear:
        if coll in COLLECTIONS:
            collection_name = COLLECTIONS[coll]
            deleted = await delete_collection(collection_name)
            total_deleted += deleted
        else:
            print(f"Unknown collection: {coll}")
    
    print(f"🏁 Operation complete. {total_deleted} total documents deleted.")
    
    if "cache" in collections_to_clear:
        print("⚠️ Note: You may want to run refresh_unknowns.py to rebuild the token cache.")
    
    if "calls" in collections_to_clear:
        print("⚠️ Warning: You have deleted all call data. Make sure you have a backup!")

async def main():
    print("🔥 Firestore Collection Cleaner 🔥")
    print("This tool will delete documents from specified Firestore collections.")
    print(f"\nAvailable collections:")
    for key, value in COLLECTIONS.items():
        print(f"  • {key} ({value})")

    # Get collections to clear
    if len(sys.argv) > 1:
        collections_to_clear = sys.argv[1:]
    else:
        collections_input = input("\nEnter collections to clear (comma separated): ")
        collections_to_clear = [c.strip() for c in collections_input.split(",")]
    
    # Validate input
    valid_collections = [c for c in collections_to_clear if c in COLLECTIONS]
    if not valid_collections:
        print("No valid collections specified. Exiting.")
        return
    
    # Confirm deletion
    print(f"\n⚠️ You are about to delete ALL documents from these collections:")
    for coll in valid_collections:
        print(f"  • {coll} ({COLLECTIONS[coll]})")
    
    print("\n⚠️ THIS ACTION CANNOT BE UNDONE! ⚠️")
    confirm = input("\nType 'YES' to confirm deletion: ")
    
    if confirm != "YES":
        print("Operation cancelled.")
        return
    
    # Add a timeout
    print("\nStarting deletion in 3 seconds...")
    for i in range(3, 0, -1):
        print(f"{i}...")
        time.sleep(1)
    
    # Perform deletion
    await clear_collections(valid_collections)

if __name__ == "__main__":
    asyncio.run(main()) 
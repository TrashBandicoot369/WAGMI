import asyncio
from lib.firebase_admin_setup import db
from firebase_admin import firestore  # Use firebase_admin.firestore instead

# Use the db from firebase_admin_setup
calls_ref = db.collection("calls")

async def fix_invalid_timestamps():
    print("🔍 Scanning for documents with invalid timestamps...")
    
    # Get all documents from the calls collection
    all_docs = list(calls_ref.stream())
    print(f"Found {len(all_docs)} documents to check")
    
    fixed_count = 0
    for doc in all_docs:
        doc_data = doc.to_dict()
        doc_id = doc.id
        
        # Check if timestamp is None or not a proper server timestamp
        timestamp = doc_data.get("timestamp")
        if timestamp is None:
            print(f"🔄 Fixing document {doc_id} with missing timestamp")
            
            # Update the document with a server timestamp
            calls_ref.document(doc_id).set({
                "timestamp": firestore.SERVER_TIMESTAMP
            }, merge=True)
            
            fixed_count += 1
    
    print(f"✅ Fixed {fixed_count} documents with invalid timestamps")

if __name__ == "__main__":
    print("✅ Firebase Admin SDK initialized successfully")
    asyncio.run(fix_invalid_timestamps())

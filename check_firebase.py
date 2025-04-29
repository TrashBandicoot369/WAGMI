import asyncio
from lib.firebase_admin_setup import db

async def check_firebase():
    print("🔍 Checking Firebase collections...")
    
    # List all collections
    collections = db.collections()
    print("Available collections:")
    for collection in collections:
        doc_count = len(list(collection.limit(1000).stream()))
        print(f"- {collection.id}: {doc_count} documents")
    
    # Check calls collection specifically
    calls = list(db.collection('calls').limit(10).stream())
    print(f"\nCalls collection has {len(calls)} documents")
    
    if calls:
        print("\nSample calls:")
        for call in calls[:3]:
            data = call.to_dict()
            print(f"- ID: {call.id}")
            print(f"  Symbol: {data.get('symbol', data.get('token', 'UNKNOWN'))}")
            print(f"  Timestamp: {data.get('timestamp')}")
            print(f"  Market Cap: ${data.get('marketCap', 'N/A')}")
            print(f"  DEX URL: {data.get('dexUrl', 'N/A')}")
            print()
    
    # Check telegram configuration
    print("\nChecking Telegram configuration...")
    try:
        from lib.telegram_api import get_bot_token, get_chat_ids
        token = get_bot_token()
        chat_ids = get_chat_ids()
        
        print(f"Bot token exists: {'Yes' if token else 'No'}")
        print(f"Chat IDs: {chat_ids if chat_ids else 'None configured'}")
    except Exception as e:
        print(f"Error checking Telegram config: {e}")
    
    # Check website data fetching (from client library)
    print("\nFrontend Firebase config exists:")
    try:
        from lib.firebase_client import db as client_db
        print("Firebase client configuration found")
    except Exception as e:
        print(f"Error with frontend firebase config: {e}")

if __name__ == "__main__":
    asyncio.run(check_firebase()) 
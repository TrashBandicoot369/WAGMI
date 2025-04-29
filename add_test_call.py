import asyncio
from lib.firebase_admin_setup import db
from google.cloud import firestore
import time

async def add_test_call():
    print("🔍 Adding test call to the calls collection...")
    
    # Create a test call
    test_call = {
        "symbol": "TEST",
        "token": "TEST",
        "dexUrl": "https://dexscreener.com/solana/GN2G7d2qWfsfG3j6CXsiHuuTN5Huzkq4dq86Y4o7yiKc",
        "contract": "GN2G7d2qWfsfG3j6CXsiHuuTN5Huzkq4dq86Y4o7yiKc",
        "timestamp": firestore.SERVER_TIMESTAMP,
        "status": "LIVE",
        "marketCap": 100000,
        "volume24h": 50000,
        "initialMarketCap": 80000,
        "athMarketCap": 150000,
        "percentChange24h": 25.5,
        "isNew": True,
        "chain": "solana",
        "shotCaller": False
    }
    
    # Add to Firestore
    db.collection("calls").add(test_call)
    print("✅ Test call added successfully!")
    print("Check your website to see if it appears in the feed.")
    
    # Wait for Firestore to update
    print("Waiting 5 seconds for Firestore to update...")
    time.sleep(5)
    
    # Verify if the call was added
    calls = list(db.collection("calls").where("symbol", "==", "TEST").limit(1).stream())
    if calls:
        print(f"✅ Verified! Test call exists with ID: {calls[0].id}")
    else:
        print("❌ Failed to verify test call in the database.")

if __name__ == "__main__":
    asyncio.run(add_test_call()) 
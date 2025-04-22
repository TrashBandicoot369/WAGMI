#!/usr/bin/env python3

from lib.firebase_admin_setup import db
import sys

def test_user_loading():
    """Test that user loading from Firestore works correctly"""
    print("🔍 Testing user loading from Firestore...")
    
    # Initialize empty user data structures
    USER_MAPPING = {}
    SHOT_CALLERS = []
    CALLERS = []
    
    # Load users from Firestore
    user_docs = db.collection("telegramUsers").stream()
    for doc in user_docs:
        uid = int(doc.id)
        user = doc.to_dict()
        USER_MAPPING[uid] = user.get("username", "Unknown")
        if user.get("role") == "SHOT_CALLER":
            SHOT_CALLERS.append(uid)
        else:
            CALLERS.append(uid)
    
    # Print results
    print(f"\n✅ Successfully loaded {len(USER_MAPPING)} users:")
    print(f"  - {len(SHOT_CALLERS)} shot callers")
    print(f"  - {len(CALLERS)} callers")
    
    # Print some sample data
    if SHOT_CALLERS:
        print("\n🧠 Sample Shot Callers:")
        for i, uid in enumerate(SHOT_CALLERS[:3]):
            print(f"  {i+1}. User ID: {uid}, Username: {USER_MAPPING.get(uid, 'Unknown')}")
    
    if CALLERS:
        print("\n📣 Sample Callers:")
        for i, uid in enumerate(CALLERS[:3]):
            print(f"  {i+1}. User ID: {uid}, Username: {USER_MAPPING.get(uid, 'Unknown')}")
    
    print("\n🎯 Test completed successfully!")

if __name__ == "__main__":
    test_user_loading() 
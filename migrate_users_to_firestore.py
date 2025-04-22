#!/usr/bin/env python3

from firebase_admin import firestore
from lib.firebase_admin_setup import db
import sys

def get_hardcoded_users():
    """Get the hardcoded users from qwant3.py"""
    # These are the original hardcoded values from qwant3.py
    USER_MAPPING = {
        837563973: "Unknown",
        7808944025: "Unknown",
        1973324576: "Unknown",
        1282880940: "Unknown",
        1634061759: "Unknown",
        6849959621: "Unknown",
        5692101176: "Unknown",
        6763993595: "Unknown",
        1665358865: "wabibi",
        1772890464: "octosea",
        1021989167: "EntityNotFound",
        7034010223: "mr_moonrunitup",
        7034413493: "robertnfa",
        963718578: "ohcharlie",
        5046008695: "edgrudskiy",
        7088866708: "Helpermicin",
        581678251: "reggyyy"
    }
    
    SHOT_CALLERS = [5337215623, 7137640996, 7538811744, 963718578, 5220299596, 6047628843, 451261430]
    CALLERS = [uid for uid in USER_MAPPING if uid not in SHOT_CALLERS]
    
    return USER_MAPPING, SHOT_CALLERS, CALLERS

def migrate_users():
    """Migrate the hardcoded users to Firestore"""
    USER_MAPPING, SHOT_CALLERS, CALLERS = get_hardcoded_users()
    
    # Count successful migrations
    success_count = 0
    
    # Migrate shot callers
    print("🔄 Migrating shot callers...")
    for user_id in SHOT_CALLERS:
        username = USER_MAPPING.get(user_id, "Unknown")
        
        try:
            db.collection("telegramUsers").document(str(user_id)).set({
                "username": username,
                "role": "SHOT_CALLER",
                "addedBy": "migration",
                "addedAt": firestore.SERVER_TIMESTAMP
            })
            print(f"✅ Added shot caller: @{username} (ID: {user_id})")
            success_count += 1
        except Exception as e:
            print(f"❌ Failed to add shot caller {user_id}: {e}")
    
    # Migrate callers
    print("\n🔄 Migrating callers...")
    for user_id in CALLERS:
        username = USER_MAPPING.get(user_id, "Unknown")
        
        try:
            db.collection("telegramUsers").document(str(user_id)).set({
                "username": username,
                "role": "CALLER",
                "addedBy": "migration",
                "addedAt": firestore.SERVER_TIMESTAMP
            })
            print(f"✅ Added caller: @{username} (ID: {user_id})")
            success_count += 1
        except Exception as e:
            print(f"❌ Failed to add caller {user_id}: {e}")
    
    print(f"\n🎉 Migration complete! Successfully migrated {success_count} out of {len(SHOT_CALLERS) + len(CALLERS)} users.")

if __name__ == "__main__":
    print("🔄 Starting user migration to Firestore...")
    
    # Ask for confirmation
    confirmation = input("This will migrate hardcoded users to Firestore. Continue? (y/n): ")
    
    if confirmation.lower() == 'y':
        migrate_users()
    else:
        print("Migration cancelled.")
        sys.exit(0) 
#!/usr/bin/env python3

from firebase_admin import firestore
import firebase_admin
from lib.firebase_admin_setup import db
import datetime

def add_or_update_user(user_id, username, role, added_by="admin"):
    """
    Add or update a Telegram user in the telegramUsers collection
    
    Parameters:
    - user_id: int - Telegram user ID
    - username: str - Telegram username
    - role: str - Either "SHOT_CALLER" or "CALLER"
    - added_by: str - Who added this user
    """
    try:
        user_ref = db.collection("telegramUsers").document(str(user_id))
        user_ref.set({
            "username": username,
            "role": role,
            "addedBy": added_by,
            "addedAt": firestore.SERVER_TIMESTAMP
        }, merge=True)
        print(f"✅ Added/updated user @{username} (ID: {user_id}) as {role}")
        return True
    except Exception as e:
        print(f"❌ Failed to add user {username}: {e}")
        return False

def migrate_existing_users():
    """
    Migrate existing users from the hardcoded lists in qwant3.py to Firestore
    """
    # Import the existing user mappings
    from qwant3 import USER_MAPPING, SHOT_CALLERS, CALLERS
    
    print("🔄 Migrating existing users to Firestore...")
    
    # Add shot callers
    for user_id in SHOT_CALLERS:
        username = USER_MAPPING.get(user_id, "Unknown")
        add_or_update_user(user_id, username, "SHOT_CALLER")
    
    # Add callers
    for user_id in CALLERS:
        username = USER_MAPPING.get(user_id, "Unknown")
        add_or_update_user(user_id, username, "CALLER")
    
    print(f"✅ Migration complete. Added {len(SHOT_CALLERS)} shot callers and {len(CALLERS)} callers.")

def add_new_user():
    """Interactive prompt to add a new user"""
    try:
        user_id = int(input("Enter Telegram user ID: "))
        username = input("Enter username (without @): ")
        role = input("Enter role (SHOT_CALLER or CALLER): ").upper()
        
        if role not in ["SHOT_CALLER", "CALLER"]:
            print("❌ Invalid role. Must be SHOT_CALLER or CALLER.")
            return
        
        added_by = input("Added by (default: admin): ") or "admin"
        
        add_or_update_user(user_id, username, role, added_by)
    except ValueError:
        print("❌ User ID must be a number")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🔥 Telegram User Management 🔥")
    print("1. Migrate existing users to Firestore")
    print("2. Add a new user")
    print("3. Exit")
    
    choice = input("Select an option: ")
    
    if choice == "1":
        migrate_existing_users()
    elif choice == "2":
        add_new_user()
    else:
        print("Exiting...") 
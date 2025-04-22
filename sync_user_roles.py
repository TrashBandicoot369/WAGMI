#!/usr/bin/env python3

from firebase_admin import firestore
from lib.firebase_admin_setup import db
import sys

def sync_user_collections():
    """
    Synchronizes users between telegramUsers and roles collections 
    to ensure consistent role assignments across the application.
    """
    print("🔄 Starting user collection synchronization...")
    
    # Get all users from telegramUsers collection
    telegram_users = {}
    telegram_users_ref = db.collection("telegramUsers")
    telegram_users_docs = telegram_users_ref.stream()
    
    for doc in telegram_users_docs:
        user_id = doc.id
        user_data = doc.to_dict()
        telegram_users[user_id] = user_data
    
    print(f"📊 Found {len(telegram_users)} users in telegramUsers collection")
    
    # Get all users from roles collection
    roles_users = {}
    roles_ref = db.collection("roles")
    roles_docs = roles_ref.stream()
    
    for doc in roles_docs:
        user_id = doc.id
        user_data = doc.to_dict()
        roles_users[user_id] = user_data
    
    print(f"📊 Found {len(roles_users)} users in roles collection")
    
    # 1. Add missing users from telegramUsers to roles
    users_to_add_to_roles = 0
    for user_id, telegram_data in telegram_users.items():
        if user_id not in roles_users:
            # User exists in telegramUsers but not in roles, add them
            try:
                roles_ref.document(user_id).set({
                    "name": telegram_data.get("username", "Unknown"),
                    "role": telegram_data.get("role", "CALLER"),
                    "createdAt": telegram_data.get("addedAt", firestore.SERVER_TIMESTAMP),
                    "addedBy": telegram_data.get("addedBy", "sync_script")
                })
                users_to_add_to_roles += 1
                print(f"✅ Added user {user_id} to roles collection")
            except Exception as e:
                print(f"❌ Failed to add user {user_id} to roles: {e}")
        else:
            # User exists in both collections, ensure role is consistent
            telegram_role = telegram_data.get("role", "CALLER")
            roles_role = roles_users[user_id].get("role", "CALLER")
            
            if telegram_role != roles_role:
                # Roles are inconsistent, update roles collection with telegramUsers role
                try:
                    roles_ref.document(user_id).update({
                        "role": telegram_role,
                        "updatedAt": firestore.SERVER_TIMESTAMP,
                        "updatedBy": "sync_script"
                    })
                    print(f"🔄 Updated user {user_id} role in roles collection from {roles_role} to {telegram_role}")
                except Exception as e:
                    print(f"❌ Failed to update user {user_id} role: {e}")
    
    # 2. Add missing users from roles to telegramUsers
    users_to_add_to_telegram = 0
    for user_id, roles_data in roles_users.items():
        if user_id not in telegram_users:
            # User exists in roles but not in telegramUsers, add them
            try:
                username = roles_data.get("name", "Unknown").lower()
                telegram_users_ref.document(user_id).set({
                    "username": username,
                    "role": roles_data.get("role", "CALLER"),
                    "addedAt": roles_data.get("createdAt", firestore.SERVER_TIMESTAMP),
                    "addedBy": roles_data.get("addedBy", "sync_script")
                })
                users_to_add_to_telegram += 1
                print(f"✅ Added user {user_id} to telegramUsers collection")
            except Exception as e:
                print(f"❌ Failed to add user {user_id} to telegramUsers: {e}")
        else:
            # User exists in both collections, ensure role is consistent
            telegram_role = telegram_users[user_id].get("role", "CALLER")
            roles_role = roles_data.get("role", "CALLER")
            
            if telegram_role != roles_role:
                # Roles are inconsistent, update telegramUsers collection with roles role
                try:
                    telegram_users_ref.document(user_id).update({
                        "role": roles_role,
                        "updatedAt": firestore.SERVER_TIMESTAMP,
                        "updatedBy": "sync_script"
                    })
                    print(f"🔄 Updated user {user_id} role in telegramUsers collection from {telegram_role} to {roles_role}")
                except Exception as e:
                    print(f"❌ Failed to update user {user_id} role: {e}")
    
    # Look specifically for user "reggyyy" with ID 581678251
    if "581678251" in telegram_users:
        print("\n🔍 Checking specific user reggyyy (ID: 581678251):")
        telegram_role = telegram_users["581678251"].get("role", "CALLER")
        print(f"  - In telegramUsers collection: role = {telegram_role}")
        
        if "581678251" in roles_users:
            roles_role = roles_users["581678251"].get("role", "CALLER")
            print(f"  - In roles collection: role = {roles_role}")
        else:
            print("  - Not found in roles collection")
    else:
        print("\n⚠️ User reggyyy (ID: 581678251) not found in telegramUsers collection")
    
    print(f"\n🎉 Synchronization complete!")
    print(f"  - Added {users_to_add_to_roles} users to roles collection")
    print(f"  - Added {users_to_add_to_telegram} users to telegramUsers collection")
    print("\nPlease restart your Telegram bot for changes to take effect.")

if __name__ == "__main__":
    # Ask for confirmation
    confirmation = input("This will synchronize users between telegramUsers and roles collections. Continue? (y/n): ")
    
    if confirmation.lower() == 'y':
        sync_user_collections()
    else:
        print("Synchronization cancelled.")
        sys.exit(0) 
#!/usr/bin/env python3

from firebase_admin import firestore
from lib.firebase_admin_setup import db
import sys

def list_users():
    """List all users in the telegramUsers collection"""
    users = db.collection("telegramUsers").stream()
    
    shot_callers = []
    callers = []
    
    for doc in users:
        user = doc.to_dict()
        user_id = doc.id
        entry = {
            "id": user_id,
            "username": user.get("username", "Unknown"),
            "addedBy": user.get("addedBy", "Unknown"),
            "addedAt": user.get("addedAt", "Unknown")
        }
        
        if user.get("role") == "SHOT_CALLER":
            shot_callers.append(entry)
        else:
            callers.append(entry)
    
    print("\n🧠 SHOT CALLERS:")
    print("-" * 60)
    print(f"{'USER ID':<15} {'USERNAME':<20} {'ADDED BY':<15} {'ADDED AT'}")
    print("-" * 60)
    for user in shot_callers:
        added_at = user["addedAt"].strftime("%Y-%m-%d %H:%M") if hasattr(user["addedAt"], "strftime") else "Unknown"
        print(f"{user['id']:<15} {user['username']:<20} {user['addedBy']:<15} {added_at}")
    
    print("\n📣 CALLERS:")
    print("-" * 60)
    print(f"{'USER ID':<15} {'USERNAME':<20} {'ADDED BY':<15} {'ADDED AT'}")
    print("-" * 60)
    for user in callers:
        added_at = user["addedAt"].strftime("%Y-%m-%d %H:%M") if hasattr(user["addedAt"], "strftime") else "Unknown"
        print(f"{user['id']:<15} {user['username']:<20} {user['addedBy']:<15} {added_at}")
    
    print(f"\nTotal users: {len(shot_callers) + len(callers)} ({len(shot_callers)} shot callers, {len(callers)} callers)")

def add_user(user_id, username, role, added_by="admin"):
    """Add a new user to the telegramUsers collection"""
    try:
        # Convert user_id to integer and validate it
        user_id = int(user_id)
        
        # Validate role
        role = role.upper()
        if role not in ["SHOT_CALLER", "CALLER"]:
            print("❌ Invalid role. Must be SHOT_CALLER or CALLER.")
            return False
        
        # Add to Firestore
        user_ref = db.collection("telegramUsers").document(str(user_id))
        user_ref.set({
            "username": username,
            "role": role,
            "addedBy": added_by,
            "addedAt": firestore.SERVER_TIMESTAMP
        })
        
        print(f"✅ Added user @{username} (ID: {user_id}) as {role}")
        return True
    except ValueError:
        print("❌ User ID must be a number")
        return False
    except Exception as e:
        print(f"❌ Error adding user: {e}")
        return False

def delete_user(user_id):
    """Delete a user from the telegramUsers collection"""
    try:
        # Convert user_id to integer for validation
        int(user_id)
        
        # Delete from Firestore
        db.collection("telegramUsers").document(str(user_id)).delete()
        print(f"✅ Deleted user with ID: {user_id}")
        return True
    except ValueError:
        print("❌ User ID must be a number")
        return False
    except Exception as e:
        print(f"❌ Error deleting user: {e}")
        return False

def update_user_role(user_id, new_role):
    """Update a user's role"""
    try:
        # Convert user_id to integer and validate it
        user_id = int(user_id)
        
        # Validate role
        new_role = new_role.upper()
        if new_role not in ["SHOT_CALLER", "CALLER"]:
            print("❌ Invalid role. Must be SHOT_CALLER or CALLER.")
            return False
        
        # Update in Firestore
        user_ref = db.collection("telegramUsers").document(str(user_id))
        user_ref.update({"role": new_role})
        
        print(f"✅ Updated user {user_id} role to {new_role}")
        return True
    except ValueError:
        print("❌ User ID must be a number")
        return False
    except Exception as e:
        print(f"❌ Error updating user role: {e}")
        return False

def print_help():
    print("""
📋 Telegram User Management Commands:

list                      - List all users
add <id> <username> <role> [added_by] - Add a new user
                          (role must be SHOT_CALLER or CALLER)
delete <id>               - Delete a user
update-role <id> <role>   - Update a user's role
                          (role must be SHOT_CALLER or CALLER)
help                      - Show this help message
    """)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print_help()
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "list":
        list_users()
    
    elif command == "add" and len(sys.argv) >= 5:
        user_id = sys.argv[2]
        username = sys.argv[3]
        role = sys.argv[4]
        added_by = sys.argv[5] if len(sys.argv) > 5 else "admin"
        add_user(user_id, username, role, added_by)
    
    elif command == "delete" and len(sys.argv) == 3:
        user_id = sys.argv[2]
        delete_user(user_id)
    
    elif command == "update-role" and len(sys.argv) == 4:
        user_id = sys.argv[2]
        new_role = sys.argv[3]
        update_user_role(user_id, new_role)
    
    elif command == "help":
        print_help()
    
    else:
        print("❌ Invalid command or missing arguments")
        print_help() 
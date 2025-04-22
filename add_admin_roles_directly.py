import firebase_admin
from firebase_admin import credentials, firestore
import sys
import os
import json
import argparse

# Path to the service account key
SERVICE_ACCOUNT_PATH = "./wagmi-crypto-calls-firebase-adminsdk-fbsvc-88527b62f1.json"

# Define known Telegram users
KNOWN_USERS = {
    'bizonacci': 191059284,
    'j1legend': 374435895,
    'le_printoor': 1058653530,
    'ohcharlie': 52381180,
    'alphameo': 1087968824,
    'sonder_crypto': 1112693797,
    'amitysol': 782123512,
}

def init_firebase():
    """Initialize Firebase Admin SDK"""
    if not os.path.exists(SERVICE_ACCOUNT_PATH):
        print(f"❌ Service account file not found at {SERVICE_ACCOUNT_PATH}")
        print("Please make sure you have the correct service account key file")
        sys.exit(1)
    
    # Initialize Firebase Admin SDK
    try:
        # Avoid reinitializing if already initialized
        if not firebase_admin._apps:
            cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
            firebase_admin.initialize_app(cred)
        
        # Get Firestore client
        db = firestore.client()
        print("✅ Successfully connected to Firestore")
        return db
    except Exception as e:
        print(f"❌ Error initializing Firebase: {e}")
        sys.exit(1)

def list_users(db):
    """List all users in the roles collection"""
    try:
        roles_ref = db.collection('roles')
        docs = roles_ref.stream()
        
        print("\n📋 Current Users in Firestore:")
        print("=" * 50)
        print(f"{'ID':<15} | {'Name':<20} | {'Role':<15}")
        print("-" * 50)
        
        user_count = 0
        for doc in docs:
            user_data = doc.to_dict()
            print(f"{doc.id:<15} | {user_data.get('name', 'N/A'):<20} | {user_data.get('role', 'N/A'):<15}")
            user_count += 1
        
        print("-" * 50)
        if user_count == 0:
            print("No users found in the roles collection")
        else:
            print(f"Total users: {user_count}")
        
    except Exception as e:
        print(f"❌ Error listing users: {e}")

def add_user(db, user_id, name, role):
    """Add a new user to the roles collection"""
    if not user_id or not name or not role:
        print("❌ User ID, name, and role are required")
        return
    
    if role not in ["CALLER", "SHOT_CALLER"]:
        print("❌ Role must be either 'CALLER' or 'SHOT_CALLER'")
        return
    
    try:
        # Convert user_id to string if it's not already
        user_id = str(user_id)
        
        # Add user to Firestore
        db.collection('roles').document(user_id).set({
            'name': name,
            'role': role,
            'createdAt': firestore.SERVER_TIMESTAMP
        })
        
        print(f"✅ Successfully added user: {name} (ID: {user_id}) as {role}")
    except Exception as e:
        print(f"❌ Error adding user: {e}")

def delete_user(db, user_id):
    """Delete a user from the roles collection"""
    if not user_id:
        print("❌ User ID is required")
        return
    
    try:
        # Convert user_id to string if it's not already
        user_id = str(user_id)
        
        # Check if the user exists
        user_ref = db.collection('roles').document(user_id)
        user = user_ref.get()
        
        if not user.exists:
            print(f"❌ User with ID {user_id} not found")
            return
        
        # Delete the user
        user_ref.delete()
        print(f"✅ Successfully deleted user with ID: {user_id}")
    except Exception as e:
        print(f"❌ Error deleting user: {e}")

def lookup_user_id(username):
    """Look up a user ID from a username"""
    # Remove @ if present and convert to lowercase
    clean_username = username.lstrip('@').lower()
    
    if clean_username in KNOWN_USERS:
        return KNOWN_USERS[clean_username]
    
    print(f"❌ Username '{username}' not found in known users")
    print("\nKnown usernames:")
    for name, user_id in KNOWN_USERS.items():
        print(f"- {name}: {user_id}")
    
    return None

def main():
    parser = argparse.ArgumentParser(description='Manage Telegram user roles in Firestore')
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # List users command
    list_parser = subparsers.add_parser('list', help='List all users')
    
    # Add user command
    add_parser = subparsers.add_parser('add', help='Add a new user')
    add_parser.add_argument('--id', help='Telegram user ID')
    add_parser.add_argument('--username', help='Telegram username (will be looked up in known users)')
    add_parser.add_argument('--name', help='Display name')
    add_parser.add_argument('--role', choices=['CALLER', 'SHOT_CALLER'], default='CALLER', help='User role')
    
    # Delete user command
    delete_parser = subparsers.add_parser('delete', help='Delete a user')
    delete_parser.add_argument('--id', required=True, help='Telegram user ID to delete')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Initialize Firebase
    db = init_firebase()
    
    # Execute command
    if args.command == 'list':
        list_users(db)
    elif args.command == 'add':
        user_id = args.id
        
        # If username is provided, try to look it up
        if args.username and not user_id:
            user_id = lookup_user_id(args.username)
            if not user_id:
                return
        
        # Use username as name if name is not provided
        name = args.name or args.username
        
        if not user_id or not name:
            print("❌ Either user ID or username AND name are required")
            return
        
        add_user(db, user_id, name, args.role)
    elif args.command == 'delete':
        delete_user(db, args.id)
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 
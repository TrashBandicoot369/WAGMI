# Telegram User Management System

The Telegram user management system has been updated to use Firestore for storing user information instead of hardcoded lists. This provides several advantages:

- User data can be updated without modifying code
- New users can be added on the fly
- Role changes can be made without redeploying
- The users collection can be managed through admin tools

## Firestore Structure

User data is stored in the `telegramUsers` collection with the following structure:

```
/telegramUsers (collection)
  [user_id] (doc ID as string)
    - username: "wabibi"
    - role: "SHOT_CALLER" or "CALLER"
    - addedBy: "mitch"
    - addedAt: Timestamp
```

## Migration

To migrate existing hardcoded users to Firestore:

```bash
python migrate_users_to_firestore.py
```

This script will:
1. Extract the hardcoded user lists from `qwant3.py`
2. Create new documents in the `telegramUsers` collection for each user
3. Set proper roles based on the original data
4. Mark all users as added by "migration"

## Managing Users

Use the `manage_telegram_users.py` script to manage Telegram users:

```bash
# List all users
python manage_telegram_users.py list

# Add a new user
python manage_telegram_users.py add 123456789 username CALLER mitch

# Delete a user
python manage_telegram_users.py delete 123456789

# Update a user's role
python manage_telegram_users.py update-role 123456789 SHOT_CALLER
```

## Testing the New System

To verify that users are loading correctly from Firestore:

```bash
python test_user_loading.py
```

This script will print information about all users loaded from the Firestore database.

## Changes to qwant3.py

The main application has been updated to load users dynamically from Firestore:

```python
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
```

This code replaces the previous hardcoded user lists. 
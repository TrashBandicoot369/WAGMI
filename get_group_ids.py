from telethon import TelegramClient
from telethon.errors import UsernameInvalidError, InviteHashInvalidError
from telethon.tl.functions.messages import ImportChatInviteRequest
import re

API_ID = 29312830
API_HASH = "24622c388a689db6cf871903fdca8c1c"

client = TelegramClient('user_session', API_ID, API_HASH)

async def get_group_id(identifier):
    try:
        # Handle invite links (e.g., "https://t.me/+abc123")
        if "t.me" in identifier:
            # Extract just the invite hash without the '+'
            invite_hash = identifier.split("/")[-1]
            print(f"Attempting to join using hash: {invite_hash}")
            
            # Try to join the group using the invite hash
            try:
                # Use the full invite link for joining
                group = await client(ImportChatInviteRequest(invite_hash.replace('+', '')))
                print(f"✅ Successfully joined group: {group.chats[0].title} | ID: {group.chats[0].id}")
                return
            except Exception as join_error:
                print(f"Join attempt failed: {type(join_error).__name__} - {join_error}")
            
            # If joining fails, try to get entity directly
            try:
                group = await client.get_entity(invite_hash)
                print(f"✅ Group: {group.title} | ID: {group.id}")
            except Exception as entity_error:
                print(f"Get entity failed: {type(entity_error).__name__} - {entity_error}")
                
                # Last resort: try to get dialog by name if possible
                try:
                    async for dialog in client.iter_dialogs():
                        if dialog.is_group or dialog.is_channel:
                            print(f"Found in dialogs: {dialog.name} | ID: {dialog.id}")
                except Exception as dialog_error:
                    print(f"Dialog search failed: {type(dialog_error).__name__} - {dialog_error}")
                
        # Handle usernames (e.g., "group_name")
        else:
            group = await client.get_entity(identifier)
            print(f"✅ Group: {group.title} | ID: {group.id}")

    except UsernameInvalidError:
        print(f"❌ Invalid username/invite link: {identifier}")
    except InviteHashInvalidError:
        print(f"❌ Invalid/expired invite link: {identifier}")
    except Exception as e:
        print(f"❌ Error: {type(e).__name__} - {e}")

# Replace with your group's actual username or invite link
groups = ["https://t.me/+789RPo-iGzljYzBh"]

with client:
    for group in groups:
        client.loop.run_until_complete(get_group_id(group))